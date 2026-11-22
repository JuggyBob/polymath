"""Run the exact Qwen eval question sets through Hermes CLI against LFM2.5.

Reuses the question lists from qwen36_knowledge_eval.py (12) and
qwen36_hard_eval.py (20) via AST, so the wording and answer keys are identical.
"""
import ast
import json
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(r"<TOOLS>")
HERMES = r"<USERPROFILE>\AppData\Local\hermes\bin\hermes.exe"
SERVER_LOG = Path(r"<TOOLS>\PolyStrata\strata-lfm25-ud-q3_k_m-64k.log")


def load_questions(path, var):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var:
                    return ast.literal_eval(node.value)
    raise RuntimeError(f"{var} not found in {path}")


def ask(prompt, usage_path):
    cmd = [HERMES, "-m", "lfm", "-z", prompt, "--reasoning", "none",
           "--usage-file", str(usage_path)]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=900)
    elapsed = round(time.time() - t0, 2)
    text = proc.stdout + "\n" + proc.stderr
    matches = re.findall(r"ANSWER:\s*([A-D]|\d+/\d+|\d+)", text, re.IGNORECASE)
    parsed = matches[-1].upper() if matches else ""
    if not parsed:
        plain = re.findall(r"(?:^|\s)([A-D]|\d+)(?:\s|[.)]|$)", proc.stdout, re.MULTILINE)
        parsed = plain[0].upper() if plain else ""
    usage = None
    if usage_path.exists():
        try:
            usage = json.loads(usage_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"parsed": parsed, "text": proc.stdout[-1500:], "stderr": proc.stderr[-600:],
            "returncode": proc.returncode, "elapsed_s": elapsed, "usage": usage}


def run_set(name, questions, outfile, sysmsg, suffix):
    results = []
    print(f"\n=== {name}: {len(questions)} questions ===", flush=True)
    for i, item in enumerate(questions):
        cat, expected, question = item
        prompt = sysmsg + "\n\n" + question + "\n\n" + suffix
        usage_path = HERE / f"_hermes_usage_{name}_{i}.json"
        if usage_path.exists():
            usage_path.unlink()
        try:
            r = ask(prompt, usage_path)
        except Exception as e:
            r = {"parsed": "", "error": str(e)}
        ok = r.get("parsed") == expected
        print(f"[{i+1:2d}/{len(questions)}] {cat:<9} {'OK  ' if ok else 'MISS'} "
              f"got={r.get('parsed')!r} want={expected!r} {r.get('elapsed_s')}s", flush=True)
        results.append({"category": cat, "expected": expected, "question": question,
                        "correct": ok, **r})
    cats = sorted({r["category"] for r in results})
    by_cat = {c: {"correct": sum(r["correct"] for r in results if r["category"] == c),
                  "total": sum(1 for r in results if r["category"] == c)} for c in cats}
    report = {"model": "LFM2.5-24B-A2B UD-Q3_K_M via Hermes CLI (64K, thinking off)",
              "date": time.strftime("%Y-%m-%d %H:%M:%S"),
              "harness": "Hermes Agent CLI v0.23.1, -m lfm -z",
              "by_category": by_cat,
              "total_correct": sum(v["correct"] for v in by_cat.values()),
              "total_questions": len(questions), "results": results}
    Path(outfile).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("--- summary ---", flush=True)
    for c, v in by_cat.items():
        print(f"{c:<10} {v['correct']}/{v['total']}", flush=True)
    print(f"TOTAL      {report['total_correct']}/{report['total_questions']}", flush=True)
    print("saved:", outfile, flush=True)
    return report


def speeds():
    if not SERVER_LOG.exists():
        return []
    rows = []
    for line in SERVER_LOG.read_text(encoding="utf-8", errors="replace").splitlines():
        if "tokens = " in line and "tok/s" in line:
            rows.append(line.strip())
    return rows[-12:]


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("easy", "both"):
        qs = load_questions(HERE / "qwen36_knowledge_eval.py", "QUESTIONS")
        run_set("easy", qs, HERE / "lfm25-hermes-easy.json",
                "You are taking a short test. Follow the answer format exactly.",
                "Reply with exactly one line: ANSWER: <letter-or-integer>. No other text.")
    if which in ("hard", "both"):
        qs = load_questions(HERE / "qwen36_hard_eval.py", "Q")
        run_set("hard", qs, HERE / "lfm25-hermes-hard.json",
                "You are taking a difficult test. Follow the answer format exactly.",
                "Reply with exactly one line: ANSWER: <letter-or-number-or-fraction>. No other text.")
    print("\n=== server speed lines ===", flush=True)
    for row in speeds():
        print(row[:220], flush=True)
