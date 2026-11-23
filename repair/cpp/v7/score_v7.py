#!/usr/bin/env python
"""Generic v7 scorer: correctness and performance scored separately.

Usage:
  python score_v7.py --fixture <dir> --solution <dir> --lang <python|cpp|rust|js> --out <json>

Test files print:
  TEST <name> PASS|FAIL
  PERF <name> <ms> PASS|FAIL   (exactly 3 runs per perf test)

Performance failures never set score_zero. Only correctness problems, test
tampering or compile failures do. A hidden test that passed on the pristine
baseline and fails on the candidate is a correctness regression and does set
score_zero, even when all visible tests still pass. Public-API drift is detected
by each fixture's test suite, not by the generic scorer.
"""
import argparse
import hashlib
import json
import shutil
import statistics
import subprocess
import tempfile
import time
from pathlib import Path
import os
import sys

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
               f'cl /EHsc /nologo /O2 {inc} {srcs} "{test_file}" /Fe:"{exe}"')
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

    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="v7-score-") as td:
        tmp = Path(td)
        base, cand, hid, basehid = tmp / "base", tmp / "cand", tmp / "hid", tmp / "basehid"
        copy_tree(pristine, base)
        copy_tree(solution, cand)
        vis_name = next(p.name for p in sorted((pristine / "tests").glob("test_*.*")))
        hname = next(p.name for p in sorted(hidden.glob("test_*.*")))
        base_pass, base_fail, base_perf, base_ok, _ = run_tests(
            base, base / "tests" / vis_name, tmp, "base", args.lang)
        # Hidden baseline: which hidden tests already pass on the pristine
        # source? A candidate that breaks one of these is a regression even
        # when every visible test still passes.
        copy_tree(pristine, basehid)
        for f in (basehid / "tests").glob("test_*.*"):
            f.unlink()
        shutil.copy(str(hidden / hname), str(basehid / "tests" / hname))
        base_hid_pass, base_hid_fail, base_hid_perf, base_hid_ok, base_hid_tail = run_tests(
            basehid, basehid / "tests" / hname, tmp, "basehid", args.lang)
        for f in (cand / "tests").glob("test_*.*"):
            if f.name != vis_name:
                f.unlink()
        vis_pass, vis_fail, vis_perf, vis_ok, vis_tail = run_tests(
            cand, cand / "tests" / vis_name, tmp, "vis", args.lang)

        copy_tree(solution, hid)
        for f in (hid / "tests").glob("test_*.*"):
            f.unlink()
        shutil.copy(str(hidden / hname), str(hid / "tests" / hname))
        hid_pass, hid_fail, hid_perf, hid_ok, hid_tail = run_tests(
            hid, hid / "tests" / hname, tmp, "hid", args.lang)

        bh = hashes(pristine / "tests")
        sh = hashes(solution / "tests")
        modified = sorted(k for k in set(bh) & set(sh) if bh[k] != sh[k])
        removed = sorted(set(bh) - set(sh))
        added = sorted(set(sh) - set(bh))
        ph_src, ch_src = hashes(pristine / "src"), hashes(solution / "src")
        ph_inc, ch_inc = hashes(pristine / "include"), hashes(solution / "include")
        files_removed = sorted((set(ph_src) - set(ch_src)) |
                               (set(ph_inc) - set(ch_inc)))
        public_api_intact = bool(vis_ok and hid_ok and not (set(ph_inc) - set(ch_inc)))
        # Visible regressions: visible tests that passed on pristine but fail
        # on the candidate. Hidden regressions: hidden tests that passed on
        # pristine but fail on the candidate. Either kind is a correctness
        # regression and forces score_zero. Performance-only failures do not.
        regressions = sorted((base_pass & (vis_fail | hid_fail)) |
                             (base_hid_pass & hid_fail))
        score_zero = bool(modified or removed or added or files_removed
                          or regressions or not vis_ok or not hid_ok)

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
            "compile": {"baseline": base_ok, "baseline_hidden": base_hid_ok,
                        "visible": vis_ok, "hidden": hid_ok},
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
            "baseline_hidden_passed": len(base_hid_pass),
            "baseline_hidden_passed_names": sorted(base_hid_pass),
            "regressions": regressions,
            "tests_modified": modified, "tests_removed": removed, "tests_added": added,
            "files_removed": files_removed, "public_api_intact": public_api_intact,
            "wall_clock_seconds": round(time.perf_counter() - started, 2),
            "visible_output_tail": vis_tail[-1000:], "hidden_output_tail": hid_tail[-1000:],
        }
    out = Path(args.out) if args.out else fixture / "score.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("\nsaved:", out)


if __name__ == "__main__":
    main()
