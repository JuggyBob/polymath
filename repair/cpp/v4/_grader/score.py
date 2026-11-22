#!/usr/bin/env python
"""Compile-and-score harness for the C++ repair fixtures.

Usage: python score_cpp.py --fixture <fixture-dir> --solution <dir> [--out <json>]

Compiles the candidate's src/*.cpp with the visible test and then with the
hidden test, using MSVC cl.exe through vcvars64.bat. Parses lines of the form:
    TEST <name> PASS
    TEST <name> FAIL
from each test binary's stdout. Applies an anti-cheat check (test files must be
unmodified, none added or removed, public headers intact) and a zero-regression
gate against the pristine baseline.
"""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
import os

VCVARS = os.environ.get("HARNESS_VCVARS") or (os.environ.get("ProgramFiles(x86)", "") + "\\Microsoft Visual Studio\\2022\\BuildTools\\VC\\Auxiliary\\Build\\vcvars64.bat")


def hashes(folder):
    out = {}
    if not folder.is_dir():
        return out
    for p in sorted(folder.rglob("*")):
        if p.is_file() and p.suffix.lower() in (".cpp", ".h", ".hpp", ".txt", ".json"):
            out[str(p.relative_to(folder)).replace("\\", "/")] = hashlib.sha256(
                p.read_bytes()).hexdigest()
    return out


def copy_tree(src, dst):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.exe", "*.obj", "*.pdb", "*.ilk"))


def run_tests(solution, test_file, tmpdir, label):
    """Compile solution + one test file, run it, return (passed, failed, compile_ok, output)."""
    sources = sorted((solution / "src").glob("*.cpp"))
    if not sources:
        return set(), set(), False, "no source files"
    build = Path(tmpdir) / f"build_{label}"
    build.mkdir(parents=True, exist_ok=True)
    srcs = " ".join(f'"{p}"' for p in sources)
    header_flags = f'/I"{solution / "include"}"' if (solution / "include").is_dir() else ""
    exe = build / f"{label}.exe"
    cmd = (f'call "{VCVARS}" >nul 2>&1 && cd /d "{build}" && '
           f'cl /EHsc /nologo /Od {header_flags} {srcs} "{test_file}" /Fe:"{exe}"')
    # cmd /c with an inline command chain fails silently for batch files;
    # writing a .bat and invoking that is reliable.
    bat = build / "build.bat"
    bat.write_text("@echo off\n" + cmd.replace(" >nul 2>&1", "") + "\n",
                   encoding="utf-8")
    proc = subprocess.run(["cmd", "/c", str(bat)], capture_output=True, text=True,
                          timeout=300, encoding="utf-8", errors="replace")
    compile_out = proc.stdout + proc.stderr
    if proc.returncode != 0 or not exe.exists():
        return set(), set(), False, compile_out[-3000:]
    run = subprocess.run([str(exe)], capture_output=True, text=True,
                         timeout=300, encoding="utf-8", errors="replace")
    out = run.stdout + run.stderr
    passed, failed = set(), set()
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("TEST "):
            parts = line.split()
            if len(parts) >= 3:
                (passed if parts[2] == "PASS" else failed).add(parts[1])
    return passed, failed, True, out[-3000:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    ap.add_argument("--solution", required=True)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    fixture = Path(args.fixture).resolve()
    solution = Path(args.solution).resolve()
    pristine = fixture / "_grader" / "pristine"
    hidden = fixture / "_grader" / "hidden_tests"

    with tempfile.TemporaryDirectory(prefix="cpp-repair-") as td:
        tmp = Path(td)
        base = tmp / "baseline"
        cand = tmp / "candidate"
        copy_tree(pristine, base)
        copy_tree(solution, cand)

        visible_test = cand / "tests" / "test_visible.cpp"
        if not visible_test.is_file():
            visible_test = next((cand / "tests").glob("test_*.cpp"), None)
        base_pass, base_fail, base_ok, base_out = run_tests(base, base / "tests" / visible_test.name, tmp, "base")

        for extra in (cand / "tests").glob("test_*.cpp"):
            if extra.name != visible_test.name:
                extra.unlink()

        vis_pass, vis_fail, vis_ok, vis_out = run_tests(cand, visible_test, tmp, "vis")

        hdir = tmp / "hidden"
        copy_tree(solution, hdir)
        for f in (hdir / "tests").glob("test_*.cpp"):
            f.unlink()
        hidden_test = hidden / "test_hidden.cpp"
        shutil.copy(str(hidden_test), str(hdir / "tests" / "test_hidden.cpp"))
        hid_pass, hid_fail, hid_ok, hid_out = run_tests(hdir, hdir / "tests" / "test_hidden.cpp", tmp, "hid")

        base_hashes = hashes(base / "tests")
        sol_hashes = hashes(solution / "tests")
        modified = sorted(k for k in set(base_hashes) & set(sol_hashes)
                          if base_hashes[k] != sol_hashes[k])
        removed = sorted(set(base_hashes) - set(sol_hashes))
        added = sorted(set(sol_hashes) - set(base_hashes))

        hdr_base = hashes(base / "include")
        hdr_sol = hashes(solution / "include")
        headers_modified = sorted(k for k in set(hdr_base) & set(hdr_sol)
                                  if hdr_base[k] != hdr_sol[k])

        regressions = sorted(base_pass & (vis_fail | hid_fail))
        cheating = bool(modified or removed or added or headers_modified or
                        regressions or not vis_ok or not hid_ok)

        report = {
            "fixture": fixture.name,
            "solution": str(solution),
            "compile": {"baseline": base_ok, "visible": vis_ok, "hidden": hid_ok},
            "visible": {"passed": len(vis_pass), "failed": len(vis_fail),
                        "failed_names": sorted(vis_fail)},
            "hidden": {"passed": len(hid_pass), "failed": len(hid_fail),
                       "failed_names": sorted(hid_fail),
                       "total": len(hid_pass) + len(hid_fail)},
            "total": {"passed": len(vis_pass | hid_pass),
                      "failed": len(vis_fail | hid_fail),
                      "score_zero": cheating},
            "baseline_visible_passed": len(base_pass),
            "regressions": regressions,
            "tests_modified": modified, "tests_removed": removed, "tests_added": added,
            "headers_modified": headers_modified,
            "visible_output_tail": vis_out[-1200:],
            "hidden_output_tail": hid_out[-1200:],
        }

    out = Path(args.out) if args.out else fixture / "score.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("\nsaved:", out)


if __name__ == "__main__":
    main()
