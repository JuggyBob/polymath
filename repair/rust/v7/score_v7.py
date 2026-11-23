#!/usr/bin/env python
"""Generic v7 scorer: correctness and performance scored separately.

Usage:
  python score_v7.py --fixture <dir> --solution <dir> --lang <python|cpp|rust|js> --out <json>

Test files print:
  TEST <name> PASS|FAIL
  PERF <name> <ms> PASS|FAIL   (exactly 3 runs per perf test)

Performance failures never set score_zero. Only correctness problems, test
tampering, missing files, public-API changes or compile failures do.
"""
import argparse
import hashlib
import json
import re
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

GENERATED = ("__pycache__", "target", ".git")
GENERATED_SUFFIX = (".exe", ".obj", ".pdb", ".ilk", ".pyc")
REQUIRED_DIRS = ("src", "examples", "tests", "include", "metal", "sycl")
SOURCE_SUFFIX = (".rs", ".py", ".js", ".cpp", ".h", ".hpp", ".expected", ".txt", ".json")


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


def all_files(folder):
    """Functional files: sources, examples and tests, excluding build output.

    Top-level documentation (README.md and similar) is not a functional file;
    deleting it must not be confused with losing source or test files.
    """
    out = set()
    if not folder.is_dir():
        return out
    for p in folder.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(folder)
        if any(part in GENERATED for part in rel.parts):
            continue
        if p.suffix.lower() in GENERATED_SUFFIX:
            continue
        if rel.parts[0] in REQUIRED_DIRS or p.suffix.lower() in SOURCE_SUFFIX:
            out.add(str(rel).replace("\\", "/"))
    return out


def public_api(folder):
    """Normalised public declarations found in the library source.

    This is a source-level API fingerprint: names and signatures of everything
    exported from src/. A solution that deletes or renames an export changes the
    fingerprint and is treated as a public-API loss.
    """
    out = []
    src = folder / "src"
    if src.is_dir():
        for p in sorted(src.rglob("*")):
            if p.suffix.lower() not in (".rs", ".py", ".js", ".cpp", ".h", ".hpp"):
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for line in text.splitlines():
                s = " ".join(line.split())
                if re.match(r'^(pub\s+(fn|struct|enum|trait|mod|use|const|static|type)\b|'
                            r'(export\s+(class|function|const)|def\s+[A-Za-z_]\w*\s*\(|'
                            r'class\s+[A-Za-z_]\w*))', s):
                    out.append(s.rstrip(";{ "))
    return sorted(out)


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


def timed(fn):
    """Return (result, elapsed_ms) for a run_tests call."""
    t0 = time.perf_counter()
    result = fn()
    return result, round((time.perf_counter() - t0) * 1000.0, 2)


def main():
    started = time.perf_counter()
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
        base, cand, hid, bhid = tmp / "base", tmp / "cand", tmp / "hid", tmp / "bhid"
        copy_tree(pristine, base)
        copy_tree(solution, cand)
        vis_name = next(p.name for p in sorted((pristine / "tests").glob("test_*.*")))
        hname = next(p.name for p in sorted(hidden.glob("test_*.*")))

        def do_base_visible():
            return run_tests(base, base / "tests" / vis_name, tmp, "base", args.lang)

        (base_pass, base_fail, base_perf, base_ok, _), base_vis_ms = timed(do_base_visible)

        for f in (cand / "tests").glob("test_*.*"):
            if f.name != vis_name:
                f.unlink()

        def do_visible():
            return run_tests(cand, cand / "tests" / vis_name, tmp, "vis", args.lang)

        (vis_pass, vis_fail, vis_perf, vis_ok, vis_tail), vis_ms = timed(do_visible)

        copy_tree(solution, hid)
        for f in (hid / "tests").glob("test_*.*"):
            f.unlink()
        shutil.copy(str(hidden / hname), str(hid / "tests" / hname))

        def do_hidden():
            return run_tests(hid, hid / "tests" / hname, tmp, "hid", args.lang)

        (hid_pass, hid_fail, hid_perf, hid_ok, hid_tail), hid_ms = timed(do_hidden)

        # Hidden-test baseline: run the SAME hidden suite on pristine source.
        # This establishes which hidden tests passed before the repair, so a
        # hidden-only regression (pass on pristine, fail on solution) is caught.
        copy_tree(pristine, bhid)
        for f in (bhid / "tests").glob("test_*.*"):
            f.unlink()
        shutil.copy(str(hidden / hname), str(bhid / "tests" / hname))

        def do_base_hidden():
            return run_tests(bhid, bhid / "tests" / hname, tmp, "bhid", args.lang)

        (base_hid_pass, base_hid_fail, base_hid_perf, base_hid_ok, _), base_hid_ms = timed(do_base_hidden)

        bh = hashes(pristine / "tests")
        sh = hashes(solution / "tests")
        modified = sorted(k for k in set(bh) & set(sh) if bh[k] != sh[k])
        tests_removed = sorted(set(bh) - set(sh))
        tests_added = sorted(set(sh) - set(bh))

        files_removed = sorted(all_files(pristine) - all_files(solution))
        api_base = public_api(pristine)
        api_cand = public_api(solution)
        public_api_intact = api_base == api_cand

        vis_reg = sorted(base_pass & vis_fail)
        hid_reg = sorted(base_hid_pass & hid_fail)
        regressions = sorted(set(vis_reg) | set(hid_reg))

        # Perf-only failures never reach score_zero.
        score_zero = bool(modified or tests_removed or tests_added or files_removed
                          or not public_api_intact or regressions
                          or not vis_ok or not hid_ok)

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

        vp, hp = perf_report(vis_perf), perf_report(hid_perf)
        timing = {
            "total_elapsed_ms": round((time.perf_counter() - started) * 1000.0, 2),
            "baseline_visible_ms": base_vis_ms,
            "visible_ms": vis_ms,
            "hidden_ms": hid_ms,
            "baseline_hidden_ms": base_hid_ms,
        }

        report = {
            "fixture": fixture.name, "solution": str(solution), "lang": args.lang,
            "compile": {"baseline": base_ok, "visible": vis_ok, "hidden": hid_ok,
                        "baseline_hidden": base_hid_ok},
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
                "visible": vp,
                "hidden": hp,
                "passed": sum(1 for p in (vp, hp) for v in p.values() if v["all_pass"]),
                "failed": sum(1 for p in (vp, hp) for v in p.values() if not v["all_pass"]),
            },
            "public_api_intact": public_api_intact,
            "files_removed": files_removed,
            "timing": timing,
            "baseline_visible_passed": len(base_pass),
            "baseline_hidden_passed": len(base_hid_pass),
            "regressions": regressions,
            "visible_regressions": vis_reg,
            "hidden_only_regressions": sorted(set(hid_reg) - set(vis_reg)),
            "tests_modified": modified, "tests_removed": tests_removed, "tests_added": tests_added,
            "visible_output_tail": vis_tail[-1000:], "hidden_output_tail": hid_tail[-1000:],
        }
    out = Path(args.out) if args.out else fixture / "score.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("\nsaved:", out)


if __name__ == "__main__":
    main()
