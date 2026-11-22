"""Run the 10 browsecomp-HARD items through Unsloth Studio's tool-enabled API.

Uses SSE streaming (non-streaming silently skips web search). Saves results
incrementally after every item so partial results survive a failure.
"""
import argparse
import json
import os
import re
import time
import datetime
import requests

BASE = r"<REPO>\closed-qa\browsecomp-hard-10"
QFILE = os.path.join(BASE, "browsecomp_hard_questions.json")
RFILE = os.path.join(BASE, "qwen36-unsloth-results.json")
KEYFILE = r"<USERPROFILE>\AppData\Local\Temp\opencode\unsloth_api_key.txt"

ENDPOINT = "http://127.0.0.1:8888/v1/chat/completions"
MODEL = "qwen3.6-35b-a3b-ud-q3_k_m"
PROVIDER_ID = "7f361f44456f495d"

SYSTEM = (
    "You are a research assistant with web_search. Research the question thoroughly "
    "using multiple searches and page reads; never answer from memory alone. Give a "
    "concise precise answer covering every part of the question, name your sources, "
    "and end with FINAL: <answer>."
)

THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


def load_results():
    if not os.path.exists(RFILE):
        return {}
    try:
        with open(RFILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("items", data) if isinstance(data, dict) else data
        if isinstance(items, list):
            return {it["id"]: it for it in items if isinstance(it, dict) and "id" in it}
        return items if isinstance(items, dict) else {}
    except Exception:
        return {}


def save_results(items):
    out = {
        "campaign": "browsecomp-hard-10 / qwen3.6 via Unsloth Studio API",
        "date": datetime.date.today().isoformat(),
        "endpoint": ENDPOINT,
        "model": MODEL,
        "provider_id": PROVIDER_ID,
        "stream": True,
        "enable_tools": True,
        "enabled_tools": ["web_search"],
        "permission_mode": "off",
        "confirm_tool_calls": False,
        "temperature": 0,
        "items": [items[k] for k in sorted(items)],
    }
    tmp = RFILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    os.replace(tmp, RFILE)


def sse_messages(resp):
    buf = []
    for raw in resp.iter_lines(decode_unicode=True):
        if raw is None:
            continue
        line = raw.rstrip("\r")
        if line == "":
            if buf:
                yield buf
                buf = []
            continue
        buf.append(line)
    if buf:
        yield buf


def parse_msg(lines):
    event = None
    datas = []
    for ln in lines:
        if ln.startswith("event:"):
            event = ln[6:].strip()
        elif ln.startswith("data:"):
            datas.append(ln[5:].strip())
        elif ln.startswith(":"):
            continue
    payload = None
    if datas:
        text = "\n".join(datas)
        if text.strip() != "[DONE]":
            try:
                payload = json.loads(text)
            except Exception:
                payload = {"_raw_text": text[:4000]}
    return event, payload


def deep_find(o, keys):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in keys and v is not None and not isinstance(v, (dict, list)):
                return v
        for v in o.values():
            r = deep_find(v, keys)
            if r is not None:
                return r
    elif isinstance(o, list):
        for v in o:
            r = deep_find(v, keys)
            if r is not None:
                return r
    return None


def content_from(p):
    if not isinstance(p, dict):
        return "", ""
    text, think = "", ""
    ch = p.get("choices")
    if isinstance(ch, list):
        for c in ch:
            if not isinstance(c, dict):
                continue
            d = c.get("delta")
            if isinstance(d, dict):
                v = d.get("content")
                if isinstance(v, str):
                    text += v
                v = d.get("reasoning_content") or d.get("reasoning")
                if isinstance(v, str):
                    think += v
            m = c.get("message")
            if isinstance(m, dict):
                v = m.get("content")
                if isinstance(v, str):
                    text += v
                v = m.get("reasoning_content") or m.get("reasoning")
                if isinstance(v, str):
                    think += v
    for key in ("content", "text", "answer", "output_text"):
        v = p.get(key)
        if isinstance(v, str) and not text:
            text += v
    return text, think


def classify(event, p):
    s = (event or "").lower()
    if isinstance(p, dict):
        for k in ("type", "event", "event_type", "kind"):
            v = p.get(k)
            if isinstance(v, str):
                s += " " + v.lower()
        if any(k in p for k in ("tool_name", "tool_call", "tool_calls", "tool_result", "execute_tool")):
            s += " tool"
    return s


def run_item(item, api_key, timeout):
    t0 = time.time()
    rec = {
        "id": item["id"],
        "question": item["q"],
        "key": item["key"],
        "min_turns": item.get("min_turns"),
        "hops": item.get("hops", []),
        "started_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "error": None,
        "timeout": False,
    }
    body = {
        "model": MODEL,
        "provider_id": PROVIDER_ID,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": item["q"]},
        ],
        "stream": True,
        "enable_tools": True,
        "enabled_tools": ["web_search"],
        "permission_mode": "off",
        "confirm_tool_calls": False,
        "temperature": 0,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_key,
        "X-Unsloth-Events": "1",
        "Accept": "text/event-stream",
    }
    answer_parts, think_parts = [], []
    tool_events, errors, event_counts = [], [], {}
    n_msgs = 0
    try:
        with requests.post(ENDPOINT, headers=headers, json=body,
                           stream=True, timeout=(15, timeout + 30)) as resp:
            rec["http_status"] = resp.status_code
            if resp.status_code != 200:
                errors.append("HTTP %s: %s" % (resp.status_code, resp.text[:2000]))
            else:
                for lines in sse_messages(resp):
                    n_msgs += 1
                    if time.time() - t0 > timeout:
                        rec["timeout"] = True
                        errors.append("hard cap %ss reached" % timeout)
                        break
                    event, p = parse_msg(lines)
                    tag = classify(event, p)
                    main_tag = (event or (p.get("type") if isinstance(p, dict) else None) or "data")
                    event_counts[str(main_tag)] = event_counts.get(str(main_tag), 0) + 1
                    if isinstance(p, dict) and (p.get("error") or "error" in tag):
                        errors.append(json.dumps(p, ensure_ascii=False)[:1500])
                    if "tool" in tag:
                        tool_events.append({
                            "event": event,
                            "type": p.get("type") if isinstance(p, dict) else None,
                            "tool_name": deep_find(p, {"tool_name", "toolName", "name", "tool"}),
                            "round_id": deep_find(p, {"round_id", "roundId", "provenance_id"}),
                            "raw": p,
                        })
                    t, th = content_from(p)
                    if t:
                        answer_parts.append(t)
                    if th:
                        think_parts.append(th)
    except Exception as exc:
        errors.append(type(exc).__name__ + ": " + str(exc)[:1500])

    answer = "".join(answer_parts)
    answer = THINK_RE.sub("", answer).strip()
    rec.update({
        "answer": answer,
        "answer_chars": len(answer),
        "thinking_chars": len("".join(think_parts)),
        "tool_events": tool_events,
        "tool_call_count": sum(1 for e in tool_events if "start" in classify(e.get("event"), e.get("raw"))) or len(tool_events),
        "n_sse_messages": n_msgs,
        "event_type_counts": event_counts,
        "errors": errors,
        "elapsed_s": round(time.time() - t0, 2),
        "finished_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    })
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=10)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    with open(KEYFILE, "r", encoding="utf-8") as f:
        api_key = f.read().strip()
    with open(QFILE, "r", encoding="utf-8") as f:
        questions = json.load(f)["questions"]

    items = load_results()
    for q in questions:
        n = int(q["id"][1:])
        if not (args.start <= n <= args.end):
            continue
        if q["id"] in items and not args.force:
            print("SKIP", q["id"], "(already recorded)", flush=True)
            continue
        print("START", q["id"], "timeout", args.timeout, flush=True)
        rec = run_item(q, api_key, args.timeout)
        items[q["id"]] = rec
        save_results(items)
        print("DONE %s elapsed=%.1fs answer_chars=%d tool_events=%d tool_calls=%d errors=%s" % (
            q["id"], rec["elapsed_s"], rec["answer_chars"], len(rec["tool_events"]),
            rec["tool_call_count"], rec["errors"][:1]), flush=True)
        print("ANSWER:", rec["answer"][:1200].replace("\n", " | "), flush=True)


if __name__ == "__main__":
    main()
