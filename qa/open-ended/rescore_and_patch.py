"""Patch an existing baseline after a scorer/question fix, without a full re-run.

Re-scores every result whose question text did not change, using the current
scorer and answer keys. Re-asks only questions whose text changed (identified
by id in REASK). Writes a new JSON alongside the original; never overwrites it.

  python rescore_and_patch.py <old-baseline.json> <new-label>
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

import run_suite as rs

ROOT = Path(__file__).resolve().parent
QDIR = ROOT / "questions"

# These four traps previously said "same as the previous circuit" and were
# unanswerable in isolation. Their text changed, so old responses are void.
REASK = {"TRAP-04", "TRAP-05", "TRAP-06", "TRAP-07"}


def current_questions():
    out = {}
    for path in QDIR.glob("*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                d = json.loads(line)
                out[d["id"]] = d
    return out


def ask(row, base_url, model, max_tokens, timeout, temperature):
    system = rs.SYSTEM_OPEN if row["type"] in ("open", "proof") else rs.SYSTEM_FIXED
    user = row["q"]
    if row["type"] in ("open", "proof"):
        user += "\n\nGive a complete answer. End with: ANSWER: <one-sentence summary>"
    else:
        user += "\n\nReply with your reasoning, then a final line: ANSWER: <answer>"
    body = json.dumps({
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": temperature, "max_tokens": max_tokens, "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(base_url, data=body,
                                 headers={"Content-Type": "application/json"})
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


def summarize(results, cats):
    by_cat = {}
    for cat in cats:
        rr = [r for r in results if r["category"] == cat]
        auto = [r for r in rr if isinstance(r.get("correct"), bool)]
        correct = sum(bool(r["correct"]) for r in auto)
        by_cat[cat] = {
            "total": len(rr), "scored": len(auto), "manual": len(rr) - len(auto),
            "correct": correct,
            "pct": round(100 * correct / len(auto), 1) if auto else None,
        }
    auto_all = [r for r in results if isinstance(r.get("correct"), bool)]
    total = {
        "total": len(results), "scored": len(auto_all),
        "manual": len(results) - len(auto_all),
        "correct": sum(bool(r["correct"]) for r in auto_all),
        "pct": round(100 * sum(bool(r["correct"]) for r in auto_all) / len(auto_all), 1)
        if auto_all else None,
        "errors": sum(r.get("scored_by") == "error" for r in results),
    }
    return by_cat, total


def main():
    old_path = Path(sys.argv[1])
    label = sys.argv[2] if len(sys.argv) > 2 else "qwen36-baseline-corrected"
    old = json.loads(old_path.read_text(encoding="utf-8"))
    qmap = current_questions()
    meta = dict(old["meta"])
    cats = meta["categories"]

    results = []
    rescored, reasked, dropped = 0, 0, 0
    for row in old["results"]:
        qid = row["id"]
        q = qmap.get(qid)
        if q is None:
            dropped += 1
            continue
        if qid in REASK:
            print(f"REASK {qid}", flush=True)
            resp = ask(q, meta["base_url"], meta["model"], meta["max_tokens"],
                       meta["timeout"], meta["temperature"])
            scored = rs.score_row(q, resp)
            scored["scored_by"] += "+reasked"
            reasked += 1
        else:
            # Re-score the stored response with current question + scorer.
            scored = rs.score_row(q, row)
            scored["content"] = row.get("content")
            scored["reasoning"] = row.get("reasoning")
            scored["timings"] = row.get("timings")
            scored["elapsed_s"] = row.get("elapsed_s")
            if qid == "OPEN-MATH-01":
                scored["scored_by"] += "+rescoped-trap"
            rescored += 1
        results.append({"id": qid, "category": row["category"], "type": row["type"],
                        "q": q["q"], "answer": q["answer"], **scored})

    by_cat, total = summarize(results, cats)
    meta.update({
        "label": label,
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "patched_from": str(old_path),
        "note": ("Hand-written suite; not official benchmark items. "
                 f"{rescored} responses re-scored with corrected rubric/trap logic; "
                 f"{reasked} unanswerable context-dependent traps re-asked; {dropped} dropped."),
    })
    report = {"meta": meta, "by_category": by_cat, "total": total, "results": results}
    out = ROOT / "baselines" / f"{label}-{time.strftime('%Y%m%d-%H%M%S')}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    rs.print_summary(report)
    print("\nrescored:", rescored, " reasked:", reasked, " dropped:", dropped)
    print("saved:", out)


if __name__ == "__main__":
    main()
