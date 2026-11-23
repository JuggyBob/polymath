#!/usr/bin/env python
"""Generic v7 scorer: correctness and performance scored separately.

Usage:
  python score_v7.py --fixture <dir> --solution <dir> --lang <python|cpp|rust|js> --out <json>

Test files print:
  TEST <name> PASS|FAIL
  PERF <name> <ms> PASS|FAIL   (exactly 3 runs per perf test)

Performance failures never set score_zero. Only correctness problems, test
tampering, source-file removal, public-API drift or compile failures do.

The pristine source is baselined on BOTH suites. A hidden test that passes on
pristine and fails on the solution is a correctness regression and is reported
in "regressions" and reflected in score_zero, even when no visible test covers
it. Performance lines never enter either set.
"""
import argparse
import hashlib
import json
import shutil
import statistics
import subprocess
import tempfile
from pathlib import Path
import os
import re
import sys
import time

PY = os.environ.get("HARNESS_PYTHON") or sys.executable
RUSTC = os.environ.get("HARNESS_RUSTC") or shutil.which("rustc") or "rustc"
VCVARS = os.environ.get("HARNESS_VCVARS") or os.path.join(
    os.environ.get("ProgramFiles(x86)", ""), "Microsoft Visual Studio", "2022",
    "BuildTools", "VC", "Auxiliary", "Build", "vcvars64.bat")
NODE = os.environ.get("HARNESS_NODE") or shutil.which("node") or "node"


def hashes(folder):
    out = {}
    if not folder.is_dir():
        return out
    for p in sorted(folder.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and p.suffix.lower() in (
                ".py", ".cpp", ".h", ".hpp", ".rs", ".js", ".txt", ".json", ".expected"):
            out[str(p.relative_to(folder)).replace("\\", "/")] = hashlib.sha256(
                p.read_bytes()).hexdigest()
    return out


def copy_tree(src, dst):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
        "__pycache__", "*.pyc", "*.exe", "*.obj", "*.pdb", "*.ilk", "target"))


def public_names(folder):
    path = folder / "src" / "vm" / "__init__.py"
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"__all__\s*=\s*\[(.*?)\]", text, re.S)
    if match is None:
        return set()
    return set(re.findall(r'"([A-Za-z_][A-Za-z0-9_]*)"', match.group(1)))


def build_command(lang, solution, test_file, exe, tmp):
    if lang == "python":
        return [PY, str(test_file)], None
    if lang == "js":
        return [NODE, str(test_file)], None
    if lang == "rust":
        cmd = [RUSTC, "--edition", "2021", "-O", str(test_file), "-o", str(exe)]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                           encoding="utf-8", errors="replace")
        if r.returncode != 0 or not exe.exists():
            return None, (r.stdout + r.stderr)[-3000:]
        return [str(exe)], None
    if lang == "cpp":
        sources = sorted((solution / "src").glob("*.cpp"))
        srcs = " ".join(f'"{p}"' for p in sources)
        inc = f'/I"{solution / "include"}"' if (solution / "include").is_dir() else ""
        build = Path(tmp) / (exe.stem + "_build")
        build.mkdir(parents=True, exist_ok=True)
        cmd = (f'call "{VCVARS}" >nul 2>&1 && cd /d "{build}" && '
               f'cl /EHsc /nologo /Od {inc} {srcs} "{test_file}" /Fe:"{exe}"')
        bat = build / "build.bat"
        bat.write_text("@echo off\n" + cmd.replace(" >nul 2>&1", "") + "\n",
                       encoding="utf-8")
        r = subprocess.run(["cmd", "/c", str(bat)], capture_output=True, text=True,
                           timeout=300, encoding="utf-8", errors="replace")
        if r.returncode != 0 or not exe.exists():
            return None, (r.stdout + r.stderr)[-3000:]
        return [str(exe)], None
    raise ValueError(lang)


def run_tests(solution, test_file, tmp, label, lang):
    exe = Path(tmp) / f"{label}.exe"
    cmd, err = build_command(lang, solution, test_file, exe, tmp)
    if cmd is None:
        return set(), set(), {}, False, err
    try:
        r = subprocess.run(cmd, cwd=str(solution), capture_output=True, text=True,
                           timeout=300, encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return set(), set(), {}, False, "TIMEOUT"
    out = (r.stdout or "") + "\n" + (r.stderr or "")
    passed, failed, perf = set(), set(), {}
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3 and parts[0] == "TEST":
            (passed if parts[2] == "PASS" else failed).add(parts[1])
        elif len(parts) >= 4 and parts[0] == "PERF":
            try:
                ms = float(parts[2])
            except ValueError:
                continue
            perf.setdefault(parts[1], []).append({"ms": ms, "ok": parts[3] == "PASS"})
    return passed, failed, perf, True, out[-2000:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--solution", required=True)
    ap.add_argument("--lang", required=True, choices=("python", "cpp", "rust", "js"))
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    fixture = Path(args.fixture).resolve()
    solution = Path(args.solution).resolve()
    pristine = fixture / "_grader" / "pristine"
    hidden = fixture / "_grader" / "hidden_tests"

    with tempfile.TemporaryDirectory(prefix="v7-score-") as td:
        tmp = Path(td)
        base, base_hidden, cand, hid = (tmp / "base", tmp / "base_hidden",
                                        tmp / "cand", tmp / "hid")
        wall_start = time.perf_counter()
        copy_tree(pristine, base)
        copy_tree(solution, cand)
        vis_name = next(p.name for p in sorted((pristine / "tests").glob("test_*.*")))
        base_pass, base_fail, base_perf, base_ok, _ = run_tests(
            base, base / "tests" / vis_name, tmp, "base", args.lang)
        wall_base = time.perf_counter() - wall_start

        # Baseline the hidden suite on the pristine source as well. A hidden
        # test that passes on pristine and fails on the solution is a real
        # correctness regression even when no visible test covers it.
        hname = next(p.name for p in sorted(hidden.glob("test_*.*")))
        copy_tree(pristine, base_hidden)
        for f in (base_hidden / "tests").glob("test_*.*"):
            f.unlink()
        shutil.copy(str(hidden / hname), str(base_hidden / "tests" / hname))
        base_hidden_pass, base_hidden_fail, _, base_hidden_ok, _ = run_tests(
            base_hidden, base_hidden / "tests" / hname, tmp, "basehid", args.lang)
        wall_base_hidden = time.perf_counter() - wall_start
        for f in (cand / "tests").glob("test_*.*"):
            if f.name != vis_name:
                f.unlink()
        vis_pass, vis_fail, vis_perf, vis_ok, vis_tail = run_tests(
            cand, cand / "tests" / vis_name, tmp, "vis", args.lang)
        wall_visible = time.perf_counter() - wall_start

        copy_tree(solution, hid)
        for f in (hid / "tests").glob("test_*.*"):
            f.unlink()
        shutil.copy(str(hidden / hname), str(hid / "tests" / hname))
        hid_pass, hid_fail, hid_perf, hid_ok, hid_tail = run_tests(
            hid, hid / "tests" / hname, tmp, "hid", args.lang)
        wall_hidden = time.perf_counter() - wall_start
        wall_total = time.perf_counter() - wall_start

        src_base = hashes(pristine / "src")
        src_cand = hashes(solution / "src")
        files_removed = sorted(set(src_base) - set(src_cand))
        public_api_intact = public_names(pristine) <= public_names(solution)

        bh = hashes(pristine / "tests")
        sh = hashes(solution / "tests")
        modified = sorted(k for k in set(bh) & set(sh) if bh[k] != sh[k])
        removed = sorted(set(bh) - set(sh))
        added = sorted(set(sh) - set(bh))
        # Correctness regressions only. Performance lines never reach the
        # failed sets, and perf failures are deliberately absent here, so a
        # purely performance-related failure cannot set score_zero.
        regressions = sorted((base_pass & vis_fail) | (base_hidden_pass & hid_fail))
        score_zero = bool(modified or removed or added or regressions
                          or files_removed or not public_api_intact
                          or not vis_ok or not hid_ok or not base_hidden_ok)

        def perf_report(p):
            out = {}
            for name, runs in p.items():
                times = [r["ms"] for r in runs]
                out[name] = {
                    "runs_ms": times,
                    "median_ms": round(statistics.median(times), 2),
                    "all_pass": all(r["ok"] for r in runs),
                    "run_count": len(runs),
                }
            return out

        report = {
            "fixture": fixture.name, "solution": str(solution), "lang": args.lang,
            "compile": {"baseline": base_ok, "visible": vis_ok, "hidden": hid_ok},
            "correctness": {
                "visible": {"passed": len(vis_pass), "failed": len(vis_fail),
                            "failed_names": sorted(vis_fail)},
                "hidden": {"passed": len(hid_pass), "failed": len(hid_fail),
                           "failed_names": sorted(hid_fail)},
                "total_passed": len(vis_pass | hid_pass),
                "total_failed": len(vis_fail | hid_fail),
                "score_zero": score_zero,
            },
            "performance": {
                "visible": perf_report(vis_perf),
                "hidden": perf_report(hid_perf),
                "passed": sum(1 for p in (perf_report(vis_perf), perf_report(hid_perf))
                              for v in p.values() if v["all_pass"]),
                "failed": sum(1 for p in (perf_report(vis_perf), perf_report(hid_perf))
                              for v in p.values() if not v["all_pass"]),
            },
            "baseline_visible_passed": len(base_pass),
            "baseline_hidden_passed": len(base_hidden_pass),
            "regressions": regressions,
            "tests_modified": modified, "tests_removed": removed, "tests_added": added,
            "files_removed": files_removed,
            "public_api_intact": public_api_intact,
            "wall_clock_seconds": {
                "baseline": round(wall_base, 3),
                "baseline_hidden": round(wall_base_hidden - wall_base, 3),
                "visible": round(wall_visible - wall_base_hidden, 3),
                "hidden": round(wall_hidden - wall_visible, 3),
                "total": round(wall_total, 3),
            },
            "visible_output_tail": vis_tail[-1000:], "hidden_output_tail": hid_tail[-1000:],
        }
    out = Path(args.out) if args.out else fixture / "score.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("\nsaved:", out)


if __name__ == "__main__":
    main()
