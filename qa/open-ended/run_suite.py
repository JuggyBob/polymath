#!/usr/bin/env python3
"""Run the 96-question open-ended QA suite against any OpenAI-compatible server.

Nothing is hardcoded: you supply the port (and optionally the model) either as
arguments or interactively when the script starts.

Examples
--------
    python run_suite.py --port 8080
    python run_suite.py --port 8094 --model my-model --label trial-1
    python run_suite.py --port 8080 --dry-run
    python run_suite.py --port 8080 --categories swe,aime --limit 5
    python run_suite.py --port 8080 --compare baselines/qwen36-baseline.json

For each question a nicely formatted reasoning file is written at the end into
``reasoning/<label>-<timestamp>/<id>.md``. It contains the question, the model's
full answer, any ``reasoning_content`` the server returned, how it was scored
and the timing information. Nothing is sent anywhere except your local server.

These are hand-written questions in the style of SWE-bench, AIME, MMLU, GPQA
and BrowseComp. They are NOT official benchmark items. Scores are comparable
only between runs that use the same model, quant, context, temperature and
max_tokens; those values are recorded in every result JSON.
"""
import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QDIR = ROOT / "questions"
DEFAULT_CATEGORIES = "swe,aime,mmlu,gpqa,open_ended,traps"
ALL_CATEGORIES = DEFAULT_CATEGORIES + ",browsecomp"


# ---------------------------------------------------------------------------
# Question loading and scoring. This logic is the source of truth for the
# suite. Do not change it without updating the baseline JSONs.
# ---------------------------------------------------------------------------

def load_questions(categories, limit=0):
    rows = []
    for cat in categories:
        path = QDIR / f"{cat}.jsonl"
        if not path.exists():
            raise SystemExit(f"missing question file: {path}")
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    if limit:
        rows = rows[:limit]
    return rows


def norm(s):
    s = str(s or "").strip().lower()
    s = s.replace("\u2212", "-").replace("\u2013", "-").replace("\u2192", "->")
    s = re.sub(r"^answer\s*:\s*", "", s)
    s = re.sub(r"\s+", "", s)
    return s.rstrip(".!;)")


def answer_text(content):
    """The text of the final ANSWER: line (or last non-empty line).

    A trap value merely discussed in the reasoning must not count as an error;
    only adopting it in the final answer does.
    """
    matches = re.findall(r"ANSWER:\s*(.+)", content or "", re.IGNORECASE)
    if matches:
        return matches[-1].strip()
    lines = [ln.strip() for ln in (content or "").splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def extract_answer(content):
    ans = answer_text(content)
    m = re.match(r"^([A-Da-d])[\).:]", ans)
    if m:
        return m.group(1).upper()
    return ans.strip()


def numeric(value):
    try:
        return float(str(value).replace(",", ""))
    except (ValueError, TypeError):
        return None


def check_fixed(row, parsed):
    got = norm(parsed)
    for alias in row["accept"]:
        if got == norm(alias):
            return True
    g = numeric(parsed)
    if g is not None:
        for alias in row["accept"]:
            a = numeric(alias)
            if a is None or a == 0:
                continue
            # Integer keys must match exactly. A 1% tolerance on an integer
            # AIME answer would accept neighbouring integers (e.g. 2330 for
            # 2333), which is wrong.
            integer_key = re.fullmatch(r"[+-]?\d+", str(alias).strip()) is not None
            if integer_key:
                if g == a:
                    return True
            elif abs(g - a) / abs(a) <= 0.001:
                return True
    return False


def check_rubric(row, content):
    text = (content or "").lower()
    detail = []
    for item in row.get("rubric", []):
        label = item["point"]
        negative = label.lower().startswith("does not") or label.startswith("!")
        matched = False
        for pat in item["patterns"]:
            p = pat[1:] if pat.startswith("!") else pat
            try:
                hit = re.search(p, text, re.IGNORECASE) is not None
            except re.error:
                hit = p.lower() in text
            if hit:
                matched = True
                break
        ok = (not matched) if negative else matched
        detail.append({"point": label, "hit": ok})
    total = len(detail)
    score = sum(d["hit"] for d in detail)
    return score, total, (score / total >= 0.8 if total else None), detail


SYSTEM_FIXED = (
    "You are taking a difficult test. Think carefully and show your reasoning. "
    "End your response with a final line in exactly this format:\n"
    "ANSWER: <your final answer>\n"
    "The final answer must be a single letter, number, or short phrase, with no explanation."
)
SYSTEM_OPEN = (
    "You are taking a difficult essay test. Give a complete, rigorous answer, "
    "with reasoning and the key facts. End your response with a final line:\n"
    "ANSWER: <one-sentence summary>"
)


def ask(row, base_url, model, max_tokens, timeout, temperature):
    system = SYSTEM_OPEN if row["type"] in ("open", "proof") else SYSTEM_FIXED
    user = row["q"]
    if row["type"] in ("open", "proof"):
        user += "\n\nGive a complete answer. End with: ANSWER: <one-sentence summary>"
    else:
        user += "\n\nReply with your reasoning, then a final line: ANSWER: <answer>"
    body = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system},
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
    elapsed = round(time.time() - t0, 2)
    msg = data["choices"][0]["message"]
    content = msg.get("content") or ""
    return {
        "content": content,
        "reasoning": msg.get("reasoning_content"),
        "timings": data.get("timings"),
        "elapsed_s": elapsed,
    }


def score_row(row, response):
    content = response.get("content", "")
    parsed = extract_answer(content)
    out = dict(response)
    out["parsed"] = parsed
    trap_hit = False
    if row.get("trap_patterns"):
        final = answer_text(content)
        pattern_hit = any(
            re.search(p, final, re.IGNORECASE) is not None
            for p in row["trap_patterns"]
        )
        # Naming the trap value while explicitly rejecting it is not a trap.
        negated = re.search(
            r"\b(not|no|never|rather than|instead of|avoid|isn't|is not|\u2260)\b",
            final, re.IGNORECASE,
        ) is not None
        trap_hit = pattern_hit and not negated
        out["trap_hit"] = trap_hit
        out["trap_label"] = row.get("trap_label", "trap value in final answer")
    if row["type"] in ("open", "proof") and row.get("rubric"):
        s, t, ok, detail = check_rubric(row, content)
        ok = bool(ok)
        if trap_hit and not ok:
            # The trap overrides only when the rubric already fails. A correct
            # answer that merely mentions the trap must not be penalised.
            out.update(rubric_score=f"{s}/{t}", rubric_detail=detail,
                       correct=False, scored_by="rubric+trap")
        else:
            out.update(rubric_score=f"{s}/{t}", rubric_detail=detail,
                       correct=ok, scored_by="rubric")
    elif row["type"] in ("open", "proof"):
        out.update(correct=None, scored_by="manual")
    else:
        out.update(correct=check_fixed(row, parsed), scored_by="fixed")
    return out


# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------

BAR_WIDTH = 24


def progress_bar(done, total):
    if total <= 0:
        return ""
    filled = round(BAR_WIDTH * done / total)
    return "[" + "#" * filled + "." * (BAR_WIDTH - filled) + "]"


def mark_for(scored):
    if scored.get("scored_by") == "error":
        return "ERROR"
    if scored.get("correct") is True:
        return "OK"
    if scored.get("correct") is None:
        return "MANUAL"
    return "MISS"


def print_header(report):
    meta = report["meta"]
    print()
    print("=" * 78)
    print("  LOCAL MODEL QA SUITE")
    print("=" * 78)
    print(f"  endpoint   : {meta['base_url']}")
    print(f"  model      : {meta['model']}")
    print(f"  label      : {meta['label']}")
    print(f"  started    : {meta['date']}")
    print(f"  questions  : {meta['scheduled']}")
    print(f"  settings   : temp={meta['temperature']}  max_tokens={meta['max_tokens']}  timeout={meta['timeout']}s")
    print("-" * 78)


def print_step(index, total, row, scored, running_ok, running_auto):
    pct = 100.0 * index / total if total else 0.0
    mark = mark_for(scored)
    got = str(scored.get("parsed", ""))[:26]
    want = str(row["answer"])[:22]
    if running_auto:
        live = f"running {running_ok}/{running_auto} ({100.0 * running_ok / running_auto:.1f}%)"
    else:
        live = "running --"
    print(
        f"  {progress_bar(index, total)} {index:>3}/{total}  {pct:5.1f}%  "
        f"{row['id']:<13} {row['category']:<10} {mark:<6} {live}"
    )
    if mark == "ERROR":
        print(f"             ! {scored.get('error', '')[:100]}")


def print_summary(report):
    meta = report["meta"]
    print("-" * 78)
    print("  FINAL SCORE")
    print("-" * 78)
    print(f"  {'category':<14} {'correct':>8}  {'scored':>7}  {'percent':>8}")
    for cat, v in report["by_category"].items():
        if v["scored"]:
            print(f"  {cat:<14} {v['correct']:>4}/{v['total']:<3}  {v['scored']:>7}  {v['pct']:>7.1f}%")
        else:
            print(f"  {cat:<14} {'manual':>8}  {'-':>7}  {'-':>8}")
    t = report["total"]
    print("-" * 78)
    if t["scored"]:
        print(f"  {'TOTAL (auto)':<14} {t['correct']:>4}/{t['scored']:<3}  {t['pct']:>18.1f}%")
    else:
        print("  TOTAL (auto): no automatically scored items")
    print(f"  manual items : {t['manual']}")
    print(f"  errors       : {t['errors']}")
    print(f"  elapsed      : {report['meta']['elapsed_wall_s']} s")
    print("=" * 78)


def compare(report, baseline_path):
    import glob
    matches = sorted(glob.glob(str(baseline_path)))
    if not matches:
        print(f"  compare: no baseline matched {baseline_path!r}")
        return
    baseline_path = matches[-1]
    base = json.loads(Path(baseline_path).read_text(encoding="utf-8"))
    bmap = {r["id"]: r for r in base["results"]}
    regressions, improvements = [], []
    for r in report["results"]:
        b = bmap.get(r["id"])
        if not b or b.get("correct") is None or r.get("correct") is None:
            continue
        if b["correct"] and not r["correct"]:
            regressions.append(r["id"])
        if not b["correct"] and r["correct"]:
            improvements.append(r["id"])
    print(f"\n  compare vs {baseline_path}")
    print("    regressions :", ", ".join(regressions) or "none")
    print("    improvements:", ", ".join(improvements) or "none")


# ---------------------------------------------------------------------------
# Reasoning files
# ---------------------------------------------------------------------------

def fenced(text, lang=""):
    return "```" + lang + "\n" + str(text or "(empty)").rstrip() + "\n```"


def write_reasoning_files(report, reasoning_dir):
    """Write one nicely formatted Markdown file per answered question."""
    reasoning_dir.mkdir(parents=True, exist_ok=True)
    written = 0
    for r in report["results"]:
        lines = []
        lines.append(f"# {r['id']} — {r['category']} ({r['type']})")
        lines.append("")
        lines.append(f"- **Model:** {report['meta']['model']}")
        lines.append(f"- **Endpoint:** {report['meta']['base_url']}")
        lines.append(f"- **Verdict:** {mark_for(r)}")
        lines.append(f"- **Scored by:** {r.get('scored_by', 'n/a')}")
        lines.append(f"- **Elapsed:** {r.get('elapsed_s', 'n/a')} s")
        lines.append("")
        lines.append("## Question")
        lines.append("")
        lines.append(fenced(r.get("q", ""), "text"))
        lines.append("")
        lines.append("## Expected answer")
        lines.append("")
        lines.append(f"`{r.get('answer', '')}`")
        aliases = [a for a in r.get("accept", []) if a != r.get("answer")]
        if aliases:
            lines.append("")
            lines.append("Accepted aliases: " + ", ".join(f"`{a}`" for a in aliases))
        lines.append("")
        lines.append("## Model's final answer")
        lines.append("")
        lines.append(f"`{r.get('parsed', '')}`")
        if r.get("rubric_score"):
            lines.append("")
            lines.append(f"Rubric: **{r['rubric_score']}**")
            for d in r.get("rubric_detail", []):
                flag = "yes" if d["hit"] else "no"
                lines.append(f"  - {d['point']}: {flag}")
        if r.get("trap_hit"):
            lines.append("")
            lines.append(f"**Trap triggered:** {r.get('trap_label', '')}")
        lines.append("")
        lines.append("## Full response")
        lines.append("")
        lines.append(fenced(r.get("content", ""), "text"))
        reasoning = r.get("reasoning")
        if reasoning:
            lines.append("")
            lines.append("## Model reasoning (`reasoning_content`)")
            lines.append("")
            lines.append(fenced(reasoning, "text"))
        timings = r.get("timings")
        if timings:
            lines.append("")
            lines.append("## Server timings")
            lines.append("")
            lines.append(fenced(json.dumps(timings, indent=2, ensure_ascii=False), "json"))
        if r.get("error"):
            lines.append("")
            lines.append("## Error")
            lines.append("")
            lines.append(fenced(r["error"], "text"))
        lines.append("")
        lines.append("---")
        lines.append("")
        safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", r["id"])
        (reasoning_dir / f"{safe}.md").write_text("\n".join(lines), encoding="utf-8")
        written += 1
    return written


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def ask_for_port():
    while True:
        raw = input("  Port of your OpenAI-compatible server (default 8080): ").strip()
        if not raw:
            return 8080
        if raw.isdigit() and 1 <= int(raw) <= 65535:
            return int(raw)
        print("    Please enter a number between 1 and 65535.")


def ask_for_model():
    raw = input("  Model id as the server knows it (blank to skip): ").strip()
    return raw or None


def main():
    ap = argparse.ArgumentParser(
        description="Run the local model QA suite. The port is supplied by you."
    )
    ap.add_argument("--port", type=int, default=None,
                    help="local server port; prompts interactively if omitted")
    ap.add_argument("--host", default="127.0.0.1",
                    help="server host (default: 127.0.0.1)")
    ap.add_argument("--base-url", default=None,
                    help="full chat-completions URL; overrides --host/--port")
    ap.add_argument("--model", default=None,
                    help="model id; prompts interactively if omitted")
    ap.add_argument("--categories", default=DEFAULT_CATEGORIES)
    ap.add_argument("--label", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--reasoning-dir", default="",
                    help="where to write per-question reasoning files")
    ap.add_argument("--compare", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--resume", default="", help="skip ids already present in this JSON")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    if args.list:
        rows = load_questions(ALL_CATEGORIES.split(","))
        c = Counter(r["category"] for r in rows)
        for k in ALL_CATEGORIES.split(","):
            print(f"{k:<14} {c.get(k, 0)}")
        print("TOTAL", len(rows))
        return

    if args.base_url:
        base_url = args.base_url
    else:
        port = args.port if args.port is not None else ask_for_port()
        base_url = f"http://{args.host}:{port}/v1/chat/completions"

    if args.dry_run:
        # Dry-run validates question files only; it makes no HTTP request and
        # must not prompt (CI runs it with stdin closed, which raises EOFError).
        model = args.model or "dry-run"
    else:
        model = args.model or ask_for_model()
        if not model:
            print("A model id is required.", file=sys.stderr)
            return 2

    cats = [c.strip() for c in args.categories.split(",") if c.strip()]
    rows = load_questions(cats, args.limit)

    if args.dry_run:
        for r in rows:
            assert r.get("id") and r.get("q") and r.get("answer"), r
            if r["type"] in ("mcq", "numeric", "short"):
                assert r["answer"] in r["accept"], (r["id"], r["accept"])
        print(f"dry-run OK: {len(rows)} questions, {len(cats)} categories")
        print(dict(Counter(r["category"] for r in rows)))
        return

    done = set()
    prior_results = []
    if args.resume:
        p = Path(args.resume)
        if p.exists():
            prior = json.loads(p.read_text(encoding="utf-8"))
            prior_results = prior["results"]
            done = {r["id"] for r in prior_results}
            print(f"resume: skipping {len(done)} already answered")

    todo = [r for r in rows if r["id"] not in done]
    label = args.label or re.sub(r"[^A-Za-z0-9_-]+", "-", model or "model")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_path = Path(args.out) if args.out else ROOT / "baselines" / f"{label}-{stamp}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    reasoning_dir = Path(args.reasoning_dir) if args.reasoning_dir else ROOT / "reasoning" / f"{label}-{stamp}"

    print_header({
        "meta": {
            "base_url": base_url, "model": model, "label": label,
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scheduled": len(todo), "temperature": args.temperature,
            "max_tokens": args.max_tokens, "timeout": args.timeout,
        }
    })

    wall0 = time.time()
    results = list(prior_results)
    auto_so_far = ok_so_far = 0
    for i, row in enumerate(todo, 1):
        try:
            resp = ask(row, base_url, model, args.max_tokens,
                       args.timeout, args.temperature)
            scored = score_row(row, resp)
        except Exception as e:
            scored = {"content": "", "parsed": "", "correct": False,
                      "scored_by": "error", "error": f"{type(e).__name__}: {e}",
                      "elapsed_s": 0, "reasoning": None, "timings": None}
        if isinstance(scored.get("correct"), bool):
            auto_so_far += 1
            ok_so_far += 1 if scored["correct"] else 0
        print_step(i, len(todo), row, scored, ok_so_far, auto_so_far)
        results.append({
            "id": row["id"], "category": row["category"],
            "type": row["type"], "q": row["q"],
            "answer": row["answer"], "accept": row.get("accept", []),
            **scored,
        })
    elapsed_wall = round(time.time() - wall0, 1)

    by_cat = {}
    for cat in cats:
        rr = [r for r in results if r["category"] == cat]
        auto = [r for r in rr if isinstance(r.get("correct"), bool)]
        by_cat[cat] = {
            "total": len(rr), "scored": len(auto), "manual": len(rr) - len(auto),
            "correct": sum(bool(r["correct"]) for r in auto),
            "pct": round(100 * sum(bool(r["correct"]) for r in auto) / len(auto), 1)
            if auto else None,
        }
    auto_all = [r for r in results if isinstance(r.get("correct"), bool)]
    errors = [r for r in results if r.get("scored_by") == "error"]
    total = {
        "total": len(results), "scored": len(auto_all),
        "manual": len(results) - len(auto_all),
        "correct": sum(bool(r["correct"]) for r in auto_all),
        "pct": round(100 * sum(bool(r["correct"]) for r in auto_all) / len(auto_all), 1)
        if auto_all else None,
        "errors": len(errors),
    }
    report = {
        "meta": {
            "label": label, "model": model, "base_url": base_url,
            "date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "categories": cats, "temperature": args.temperature,
            "max_tokens": args.max_tokens, "timeout": args.timeout,
            "elapsed_wall_s": elapsed_wall,
            "note": "Hand-written suite; not official benchmark items.",
        },
        "by_category": by_cat, "total": total, "results": results,
    }
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    n_reasoning = write_reasoning_files(report, reasoning_dir)
    print_summary(report)
    if args.compare:
        compare(report, args.compare)
    print(f"\n  result JSON : {out_path}")
    print(f"  reasoning   : {reasoning_dir}  ({n_reasoning} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
