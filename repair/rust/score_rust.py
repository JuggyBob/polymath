#!/usr/bin/env python
"""Scorer for Rust repair fixtures: rustc compile + run, parse TEST lines.

Usage: python score_rust.py --fixture <dir> --solution <dir> [--out <json>]
"""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
import os
import shutil

RUSTC = os.environ.get("HARNESS_RUSTC") or shutil.which("rustc") or "rustc"


def hashes(folder):
    out = {}
    if not folder.is_dir():
        return out
    for p in sorted(folder.rglob("*")):
        if p.is_file() and p.suffix.lower() in (".rs", ".toml", ".txt", ".json"):
            out[str(p.relative_to(folder)).replace("\\", "/")] = hashlib.sha256(
                p.read_bytes()).hexdigest()
    return out


def copy_tree(src, dst):
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("*.exe", "*.pdb", "target"))


def run_tests(solution, test_file, tmpdir, label):
    exe = Path(tmpdir) / f"{label}.exe"
    cmd = [RUSTC, "--edition", "2021", "-O", str(test_file), "-o", str(exe)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                          encoding="utf-8", errors="replace")
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode != 0 or not exe.exists():
        return set(), set(), False, out[-3000:]
    run = subprocess.run([str(exe)], capture_output=True, text=True, timeout=300,
                         encoding="utf-8", errors="replace")
    out = (run.stdout or "") + "\n" + (run.stderr or "")
    passed, failed = set(), set()
    for line in out.splitlines():
        parts = line.strip().split()
        if len(parts) >= 3 and parts[0] == "TEST":
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

    with tempfile.TemporaryDirectory(prefix="rust-repair-") as td:
        tmp = Path(td)
        base, cand, hid = tmp / "base", tmp / "cand", tmp / "hid"
        copy_tree(pristine, base)
        copy_tree(solution, cand)
        vis_name = next(p.name for p in sorted((pristine / "tests").glob("test_*.rs")))
        base_pass, _, base_ok, _ = run_tests(base, base / "tests" / vis_name, tmp, "base")
        # Pristine hidden baseline, compiled in its own temp copy so the
        # candidate is never used as the baseline.
        baseh = tmp / "baseh"
        copy_tree(pristine, baseh)
        for f in (baseh / "tests").glob("test_*.rs"):
            f.unlink()
        shutil.copy(str(hidden / "test_hidden.rs"), str(baseh / "tests" / "test_hidden.rs"))
        base_hidden_pass, _, base_hidden_ok, _ = run_tests(
            baseh, baseh / "tests" / "test_hidden.rs", tmp, "baseh")
        for f in (cand / "tests").glob("test_*.rs"):
            if f.name != vis_name:
                f.unlink()
        vis_pass, vis_fail, vis_ok, vis_out = run_tests(cand, cand / "tests" / vis_name, tmp, "vis")

        copy_tree(solution, hid)
        for f in (hid / "tests").glob("test_*.rs"):
            f.unlink()
        shutil.copy(str(hidden / "test_hidden.rs"), str(hid / "tests" / "test_hidden.rs"))
        hid_pass, hid_fail, hid_ok, hid_out = run_tests(hid, hid / "tests" / "test_hidden.rs", tmp, "hid")

        base_h = hashes(pristine / "tests")
        sol_h = hashes(solution / "tests")
        modified = sorted(k for k in set(base_h) & set(sol_h) if base_h[k] != sol_h[k])
        removed = sorted(set(base_h) - set(sol_h))
        added = sorted(set(sol_h) - set(base_h))
        regressions = sorted(base_pass & (vis_fail | hid_fail))
        # Hidden-only regressions must also zero: break anything that passed
        # on the pristine library, visible or hidden.
        regressions = sorted(set(regressions) | (base_hidden_pass & hid_fail))
        score_zero = bool(modified or removed or added or regressions or
                          not vis_ok or not hid_ok)
        report = {
            "fixture": fixture.name, "solution": str(solution),
            "compile": {"visible": vis_ok, "hidden": hid_ok},
            "visible": {"passed": len(vis_pass), "failed": len(vis_fail), "failed_names": sorted(vis_fail)},
            "hidden": {"passed": len(hid_pass), "failed": len(hid_fail),
                       "total": len(hid_pass) + len(hid_fail), "failed_names": sorted(hid_fail)},
            "total": {"passed": len(vis_pass | hid_pass), "failed": len(vis_fail | hid_fail),
                      "score_zero": score_zero},
            "baseline_visible_passed": len(base_pass),
            "regressions": regressions, "tests_modified": modified,
            "tests_removed": removed, "tests_added": added,
            "visible_output_tail": vis_out[-1200:], "hidden_output_tail": hid_out[-1200:],
        }
    out = Path(args.out) if args.out else fixture / "score.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("\nsaved:", out)


if __name__ == "__main__":
    main()
