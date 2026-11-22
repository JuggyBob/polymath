"""Score a repair-task run.

Usage: python score.py <task_dir> [hidden_dir]

Writes a JSON report to stdout and <task_dir>/score.json.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys


IGNORE_DIRS = {"__pycache__", "_hidden_check", ".git"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def snapshot(root):
    out = {}
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in files:
            full = os.path.join(base, name)
            rel = os.path.relpath(full, root).replace("\\", "/")
            out[rel] = sha256(full)
    return out


def run_tests(task_dir, start_dir):
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", start_dir, "-v"],
        cwd=task_dir,
        capture_output=True,
        text=True,
        timeout=300,
    )
    text = (proc.stdout or "") + (proc.stderr or "")
    results = {"ok": 0, "FAIL": 0, "ERROR": 0}
    for line in text.splitlines():
        m = re.search(r"\.\.\. (ok|FAIL|ERROR|skipped)", line)
        if m:
            status = m.group(1)
            if status == "ok":
                results["ok"] += 1
            elif status in ("FAIL", "ERROR"):
                results[status] += 1
    return {
        "returncode": proc.returncode,
        "passed": results["ok"],
        "failed": results["FAIL"] + results["ERROR"],
        "output": text[-8000:],
    }


def main():
    if len(sys.argv) < 2:
        print("usage: python score.py <task_dir> [hidden_dir]")
        return 2
    task_dir = os.path.abspath(sys.argv[1])
    hidden_dir = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else None

    baseline_path = os.path.join(task_dir, "baseline.json")
    baseline = {}
    if os.path.exists(baseline_path):
        with open(baseline_path, "r", encoding="utf-8") as f:
            baseline = json.load(f).get("files", {})

    before = snapshot(task_dir)
    visible = run_tests(task_dir, "tests")

    hidden = None
    if hidden_dir:
        dest = os.path.join(task_dir, "_hidden_check")
        if os.path.isdir(dest):
            shutil.rmtree(dest)
        os.makedirs(dest)
        for name in os.listdir(hidden_dir):
            if name.endswith(".py"):
                shutil.copy2(os.path.join(hidden_dir, name), os.path.join(dest, name))
        hidden = run_tests(task_dir, "_hidden_check")
        shutil.rmtree(dest, ignore_errors=True)

    after = snapshot(task_dir)
    tracked = {k: v for k, v in after.items() if k != "score.json" and not k.startswith("_hidden_check/")}
    changed = sorted(k for k, v in tracked.items() if k in baseline and baseline[k] != v)
    added = sorted(k for k in tracked if k not in baseline and k != "baseline.json")
    removed = sorted(k for k in baseline if k not in tracked)
    tests_changed = [k for k in changed if k.startswith("tests/")]

    report = {
        "task_dir": task_dir,
        "visible": {k: v for k, v in visible.items() if k != "output"},
        "hidden": {k: v for k, v in (hidden or {}).items() if k != "output"} if hidden else None,
        "tests_modified": tests_changed,
        "files_changed": changed,
        "files_added": added,
        "files_removed": removed,
        "visible_failures": [
            line.strip()
            for line in visible["output"].splitlines()
            if line.startswith("FAIL:") or line.startswith("ERROR:")
        ],
        "hidden_failures": [
            line.strip()
            for line in (hidden["output"].splitlines() if hidden else [])
            if line.startswith("FAIL:") or line.startswith("ERROR:")
        ],
    }

    with open(os.path.join(task_dir, "score.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
