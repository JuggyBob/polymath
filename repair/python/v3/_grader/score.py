#!/usr/bin/env python
"""Score a repair-fixture-v3 candidate.

  python score.py                       # score ./task (default)
  python score.py --solution <dir>      # score a candidate copy
  python score.py --out <file.json>     # choose the output path

The scorer:
  1. Runs the visible tests on a pristine copy to learn which tests pass at baseline.
  2. Runs the visible tests on the candidate.
  3. Injects the hidden tests and runs the combined suite.
  4. Checks that tests/ was not modified, no files were removed, and the public
     API still exists.
  5. Applies a zero-regression gate: any baseline-passing test that now fails
     makes the whole task score zero.

Nothing under --solution is modified. All work happens in a temporary directory.
"""
import argparse
import ast
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRISTINE = ROOT / "_grader" / "pristine"
HIDDEN = ROOT / "_grader" / "hidden_tests"
LINE = re.compile(r"^(test_\S+)\s+\([^)]*\)\s+\.\.\.\s+(ok|FAIL|ERROR)")


def run_tests(cwd, timeout=300):
    """Return (passed_names, failed_names, returncode) from unittest discover."""
    cmd = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True,
                              timeout=timeout)
        out = proc.stdout + "\n" + proc.stderr
        rc = proc.returncode
    except subprocess.TimeoutExpired:
        return set(), {"TIMEOUT"}, 124
    passed, failed = set(), set()
    for line in out.splitlines():
        m = LINE.match(line.strip())
        if not m:
            continue
        name, status = m.group(1), m.group(2)
        if status == "ok":
            passed.add(name)
        else:
            failed.add(name)
    return passed, failed, rc


def file_hashes(folder):
    out = {}
    for p in sorted(folder.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            out[str(p.relative_to(folder)).replace("\\", "/")] = hashlib.sha256(
                p.read_bytes()).hexdigest()
    return out


def snapshot_workspace(src, dest):
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))


def count_hidden_tests():
    total = 0
    for path in HIDDEN.glob("test_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and node.name.startswith("test_"):
                total += 1
    return total


def public_api_present(candidate):
    sys.path.insert(0, str(candidate))
    try:
        from scheduler import Job, Scheduler  # noqa: F401
        for name in ("add", "get", "all_jobs", "set_priority", "cancel",
                     "pending", "next_job", "pop", "expire", "ttl_remaining",
                     "find", "batch", "snapshot", "clear"):
            if not hasattr(Scheduler, name):
                return False
        from scheduler import metrics  # noqa: F401
        for name in ("load", "oldest", "expiring", "by_priority", "slow_score"):
            if not hasattr(metrics, name):
                return False
        return True
    except Exception:
        return False
    finally:
        sys.path.remove(str(candidate))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solution", default=str(ROOT / "task"))
    ap.add_argument("--out", default=str(ROOT / "score.json"))
    args = ap.parse_args()

    solution = Path(args.solution).resolve()
    if not solution.is_dir():
        raise SystemExit(f"not a directory: {solution}")

    with tempfile.TemporaryDirectory(prefix="repair-v3-") as td:
        tmp = Path(td)
        base = tmp / "baseline"
        cand = tmp / "candidate"

        snapshot_workspace(PRISTINE, base)
        base_pass, _, _ = run_tests(base)

        snapshot_workspace(solution, cand)
        # Remove candidate-supplied test files for the visible run so they
        # cannot pollute the visible block. tests_added is still recorded from
        # the real solution directory below.
        base_test_names = set(file_hashes(base / "tests"))
        for extra in (cand / "tests").glob("*"):
            if extra.is_file() and "__pycache__" not in extra.parts:
                rel = str(extra.relative_to(cand / "tests")).replace("\\", "/")
                if rel not in base_test_names:
                    extra.unlink()
        vis_pass, vis_fail, vis_rc = run_tests(cand)

        shutil.copytree(HIDDEN, cand / "tests", dirs_exist_ok=True)
        all_pass, all_fail, all_rc = run_tests(cand)
        hid_pass = all_pass - vis_pass
        hid_fail = all_fail - vis_fail

        regressions = sorted((base_pass & (vis_fail | hid_fail)))

        base_hashes = file_hashes(base / "tests")
        cand_hashes = file_hashes(solution / "tests")
        tests_modified = sorted(k for k in set(base_hashes) & set(cand_hashes)
                                if base_hashes[k] != cand_hashes[k])
        tests_removed = sorted(set(base_hashes) - set(cand_hashes))
        # A candidate must not ship its own test files. They are removed from
        # the temp copy before the visible run; tests_added still records them.
        tests_added = sorted(set(cand_hashes) - set(base_hashes))

        base_files = set(file_hashes(base))
        cand_files = set(file_hashes(solution))
        files_removed = sorted(base_files - cand_files)

        api_ok = public_api_present(cand)
        cheating = bool(tests_modified or tests_removed or tests_added
                        or files_removed or not api_ok or regressions)

        total_hidden = count_hidden_tests()
        report = {
            "task": "repair-fixture-v3:job-scheduler",
            "solution": str(solution),
            "visible": {
                "returncode": vis_rc,
                "passed": len(vis_pass),
                "failed": len(vis_fail),
                "failed_names": sorted(vis_fail),
            },
            "hidden": {
                "returncode": all_rc,
                "passed": len(hid_pass),
                "failed": len(hid_fail),
                "failed_names": sorted(hid_fail),
                "total": total_hidden,
            },
            "total": {
                "passed": len(vis_pass | hid_pass),
                "failed": len(vis_fail | hid_fail),
                "score_zero": cheating,
            },
            "baseline_visible_passed": len(base_pass),
            "regressions": regressions,
            "tests_modified": tests_modified,
            "tests_removed": tests_removed,
            "tests_added": tests_added,
            "files_removed": files_removed,
            "public_api_intact": api_ok,
        }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    print("\nsaved:", out)


if __name__ == "__main__":
    main()
