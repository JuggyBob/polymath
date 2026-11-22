#!/usr/bin/env python3
"""Run a closed-book QA set against any OpenAI-compatible server.

Each subfolder (easy-mixed-12, hard-mixed-20, ...) is standalone: it contains
its own ``questions.jsonl`` and a copy of this runner. You supply the port.

    python run_closed_book.py --port 8080
    python run_closed_book.py --port 8094 --model my-model --label trial-1
    python run_closed_book.py --port 8080 --dry-run

A Markdown file per question is written to ``reasoning/<label>-<timestamp>/``
with the question, the full answer, any ``reasoning_content``, the score and
the server timings.

These are hand-written questions in the style of SWE-bench, GPQA, AIME and
MMLU. They are NOT official benchmark items.
"""
import argparse
import json
import re
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QFILE = ROOT / "questions.jsonl"


def load_questions(limit=0):
    rows = []
    for line in QFILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows[:limit] if limit else rows


def norm(s):
    s = str(s or "").strip().lower()
    s = s.replace("\u2212", "-").replace("\u2013", "-").replace("\u2192", "->")
    s = re.sub(r"^answer\s*:\s*", "", s)
    s = re.sub(r"\s+", "", s)
    return s.rstrip(".!;)")


def answer_text(content):
    matches = re.findall(r"ANSWER:\s*(.+)", content or "", re.IGNORECASE)
    if matches:
        return matches[-1].strip()
    lines = [ln.strip() for ln in (content or "").splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def extract_answer(content):
    ans = answer_text(content)
    m = re.match(r"^([A-Da-d])[\).:]", ans)
    return m.group(1).upper() if m else ans.strip()


def numeric(value):
    try:
        return float(str(value).replace(",", ""))
    except (ValueError, TypeError):
        return None


def check_fixed(row, parsed):
    got = norm(parsed)
    for alias in row.get("accept", [row["answer"]]):
        if got == norm(alias):
            return True
    g = numeric(parsed)
    if g is not None:
        for alias in row.get("accept", [row["answer"]]):
            a = numeric(alias)
            if a is None or a == 0:
                continue
            # Integer keys must match exactly; 1% tolerance would accept a
            # neighbouring integer answer.
            if re.fullmatch(r"[+-]?\d+", str(alias).strip()):
                if g == a:
                    return True
            elif abs(g - a) / abs(a) <= 0.001:
                return True
    return False


SYSTEM = (
    "You are taking a difficult test. Think carefully and show your reasoning. "
    "End your response with a final line in exactly this format:\n"
    "ANSWER: <your final answer>\n"
    "The final answer must be a single letter, number, or short phrase."
)


def ask(row, base_url, model, max_tokens, timeout, temperature):
    user = row["q"] + "\n\nReply with your reasoning, then a final line: ANSWER: <answer>"
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        base_url, data=body, headers={"Content-Type": "application/json"}
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.load(resp)
    msg = data["choices"][0]["message"]
    return {
        "content": msg.get("content") or "",
        "reasoning": msg.get("reasoning_content"),
        "timings": data.get("timings"),
        "elapsed_s": round(time.time() - t0, 2),
    }


def bar(done, total, width=24):
    filled = round(width * done / total) if total else 0
    return "[" + "#" * filled + "." * (width - filled) + "]"


def fenced(text, lang=""):
    return "```" + lang + "\n" + str(text or "(empty)").rstrip() + "\n```"


def write_reasoning(report, directory):
    directory.mkdir(parents=True, exist_ok=True)
    for r in report["results"]:
        verdict = "ERROR" if r.get("scored_by") == "error" else ("OK" if r.get("correct") else "MISS")
        lines = [
            f"# {r['id']} — {r['category']}",
            "",
            f"- **Model:** {report['meta']['model']}",
            f"- **Endpoint:** {report['meta']['base_url']}",
            f"- **Verdict:** {verdict}",
            f"- **Elapsed:** {r.get('elapsed_s', 'n/a')} s",
            "",
            "## Question", "", fenced(r.get("q", ""), "text"), "",
            "## Expected answer", "", f"`{r.get('answer', '')}`", "",
            "## Model's final answer", "", f"`{r.get('parsed', '')}`", "",
            "## Full response", "", fenced(r.get("content", ""), "text"), "",
        ]
        if r.get("reasoning"):
            lines += ["## Model reasoning (`reasoning_content`)", "", fenced(r["reasoning"], "text"), ""]
        if r.get("timings"):
            lines += ["## Server timings", "", fenced(json.dumps(r["timings"], indent=2, ensure_ascii=False), "json"), ""]
        if r.get("error"):
            lines += ["## Error", "", fenced(r["error"], "text"), ""]
        lines.append("---")
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", r["id"])
        (directory / f"{safe}.md").write_text("\n".join(lines), encoding="utf-8")


def ask_port():
    while True:
        raw = input("  Port of your OpenAI-compatible server (default 8080): ").strip()
        if not raw:
            return 8080
        if raw.isdigit() and 1 <= int(raw) <= 65535:
            return int(raw)
        print("    Enter a number between 1 and 65535.")


def main():
    ap = argparse.ArgumentParser(description="Run a closed-book QA set.")
    ap.add_argument("--port", type=int, default=None)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--model", default=None)
    ap.add_argument("--label", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.base_url:
        base_url = args.base_url
    else:
        port = args.port if args.port is not None else ask_port()
        base_url = f"http://{args.host}:{port}/v1/chat/completions"
    # Dry-run validates question files only; it makes no HTTP request and must
    # not prompt (CI runs it with stdin closed, which raises EOFError).
    model = args.model or ("dry-run" if args.dry_run else input("  Model id as the server knows it: ").strip())

    rows = load_questions(args.limit)
    if args.dry_run:
        for r in rows:
            assert r.get("id") and r.get("q") and r.get("answer"), r
            assert r["answer"] in r.get("accept", [r["answer"]]), r["id"]
        print(f"dry-run OK: {len(rows)} questions from {QFILE.name}")
        return 0
    if not model:
        print("A model id is required.", file=sys.stderr)
        return 2

    label = args.label or re.sub(r"[^A-Za-z0-9_-]+", "-", model)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path = ROOT / f"results-{label}-{stamp}.json"
    reasoning_dir = ROOT / "reasoning" / f"{label}-{stamp}"

    print()
    print("=" * 78)
    print("  CLOSED-BOOK QA RUN")
    print("=" * 78)
    print(f"  endpoint  : {base_url}")
    print(f"  model     : {model}")
    print(f"  questions : {len(rows)}")
    print("-" * 78)

    results, wall0, ok, n_auto = [], time.time(), 0, 0
    for i, row in enumerate(rows, 1):
        try:
            resp = ask(row, base_url, model, args.max_tokens, args.timeout, args.temperature)
            parsed = extract_answer(resp["content"])
            correct = check_fixed(row, parsed)
            scored = {**resp, "parsed": parsed, "correct": correct, "scored_by": "fixed"}
        except Exception as e:
            scored = {"content": "", "parsed": "", "correct": False,
                      "scored_by": "error", "error": f"{type(e).__name__}: {e}",
                      "elapsed_s": 0, "reasoning": None, "timings": None}
        n_auto += 1
        ok += 1 if scored["correct"] else 0
        mark = "ERROR" if scored["scored_by"] == "error" else ("OK" if scored["correct"] else "MISS")
        print(f"  {bar(i, len(rows))} {i:>3}/{len(rows)}  {row['id']:<14} "
              f"{row['category']:<8} {mark:<6} running {ok}/{n_auto}")
        results.append({"id": row["id"], "category": row["category"], **row, **scored})

    elapsed = round(time.time() - wall0, 1)
    by_cat = {}
    for cat in sorted({r["category"] for r in results}):
        rr = [r for r in results if r["category"] == cat]
        by_cat[cat] = {"total": len(rr), "correct": sum(bool(r["correct"]) for r in rr),
                       "pct": round(100 * sum(bool(r["correct"]) for r in rr) / len(rr), 1)}
    report = {
        "meta": {"model": model, "base_url": base_url, "label": label,
                 "date": time.strftime("%Y-%m-%d %H:%M:%S"), "elapsed_wall_s": elapsed,
                 "temperature": args.temperature, "max_tokens": args.max_tokens,
                 "note": "Hand-written questions; not official benchmark items."},
        "by_category": by_cat,
        "total": {"correct": ok, "total": n_auto,
                  "pct": round(100 * ok / n_auto, 1) if n_auto else None},
        "results": results,
    }
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    write_reasoning(report, reasoning_dir)

    print("-" * 78)
    print("  FINAL SCORE")
    print("-" * 78)
    print(f"  {'category':<12} {'correct':>10}  {'percent':>8}")
    for cat, v in by_cat.items():
        print(f"  {cat:<12} {v['correct']:>5}/{v['total']:<4}  {v['pct']:>7.1f}%")
    print("-" * 78)
    print(f"  {'TOTAL':<12} {ok:>5}/{n_auto:<4}  {report['total']['pct']:>7.1f}%")
    print(f"  elapsed {elapsed}s")
    print("=" * 78)
    print(f"  result JSON : {out_path}")
    print(f"  reasoning   : {reasoning_dir} ({len(results)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
