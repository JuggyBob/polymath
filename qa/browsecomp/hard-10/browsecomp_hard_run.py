"""BrowseComp-style multi-hop test: 10 research questions through Goose with LIVE web tools.

Adapted from browsecomp-web-10/browsecomp_run.py. The question file is local to
this directory and the default turn budget is 20 because these items require
several dependent searches.

Usage: python browsecomp_hard_run.py <provider> <label> <server_log> [max_turns]
"""
import ctypes
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(r"<REPO>\closed-qa\browsecomp-hard-10")
GOOSE = r"<APPS>\Goose\app\resources\bin\goose.exe"
WEB_EXT = r"web:<STRATA>\.venv\Scripts\python.exe <REPO>\closed-qa\browsecomp-web-10\web_mcp_server.py"
provider, label = sys.argv[1], sys.argv[2]
server_log = Path(sys.argv[3])
MAX_TURNS = sys.argv[4] if len(sys.argv) > 4 else "20"

data = json.loads((HERE / "browsecomp_hard_questions.json").read_text(encoding="utf-8"))
QUESTIONS = data["questions"]
SYSMSG = data["system"]

env = os.environ.copy()
env.update({
    "GOOSE_PROVIDER": provider,
    "GOOSE_TELEMETRY_ENABLED": "false",
    "GOOSE_MODE": "auto",
    "GOOSE_DISABLE_SESSION_NAMING": "true",
    "GOOSE_RANDOM_THINKING_MESSAGES": "false",
    "PYTHONIOENCODING": "utf-8",
})


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def mem():
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return (round((m.ullTotalPageFile - m.ullAvailPageFile) / 2**30, 1),
            round(m.ullAvailPhys / 2**30, 1))


_st = {"max_commit": 0.0, "min_free": 999.0, "samples": 0, "stop": False}


def sampler():
    while not _st["stop"]:
        c, f = mem()
        _st["max_commit"] = max(_st["max_commit"], c)
        _st["min_free"] = min(_st["min_free"], f)
        _st["samples"] += 1
        time.sleep(3)


threading.Thread(target=sampler, daemon=True).start()


def speed_lines(before):
    try:
        lines = server_log.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return []
    return [l.strip() for l in lines[before:] if "strata serve: prompt" in l and "tok/s" in l]


def extract(raw):
    """Parse Goose --output-format json: strip banner, find final assistant text."""
    try:
        s = raw[raw.index("{"):]
        d = json.loads(s)
    except Exception as e:
        return {"answer": "", "parse_error": str(e), "raw_tail": raw[-600:],
                "tools": [], "meta": None}
    text = ""
    tools = []
    for m in d.get("messages", []):
        if m.get("role") != "assistant":
            continue
        for c in m.get("content", []):
            if c.get("type") == "text":
                text = c.get("text", "")
            elif c.get("type") == "toolRequest":
                tc = c.get("toolCall", {}).get("value", {})
                tools.append(tc.get("name", "?"))
    return {"answer": text.strip(), "tools": tools, "meta": d.get("metadata")}


def ask(question):
    cmd = [GOOSE, "run", "--no-session", "--no-profile", "--output-format", "json",
           "--max-turns", MAX_TURNS, "--with-extension", WEB_EXT,
           "--system", SYSMSG, "-t", question]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", env=env, timeout=600)
        out, err, rc = p.stdout or "", p.stderr or "", p.returncode
    except subprocess.TimeoutExpired:
        out, err, rc = "", "", "TIMEOUT"
    r = extract(out)
    r["elapsed_s"] = round(time.time() - t0, 1)
    r["returncode"] = rc
    r["stderr"] = err[-400:]
    return r


if __name__ == "__main__":
    c0, f0 = mem()
    print(f"RUN {label} {provider} RAM start commit={c0} free={f0}", flush=True)
    before = len(server_log.read_text(encoding="utf-8", errors="replace").splitlines())
    results = []
    for item in QUESTIONS:
        r = ask(item["q"])
        row = {"id": item["id"], "tier": item["tier"], "topic": item["topic"],
               "min_turns": item["min_turns"], "hops": item["hops"],
               "question": item["q"], "key": item["key"],
               "sources": item["sources"], **r}
        results.append(row)
        ntools = len(r.get("tools", []))
        print(f"[{item['id']} min={item['min_turns']:<2}] {r['elapsed_s']}s rc={r['returncode']} "
              f"tools={ntools} ans={r['answer'][-170:]!r}", flush=True)
        HERE.joinpath(f"browsecomp-hard-{label}.json").write_text(
            json.dumps({"label": label, "results": results}, indent=2), encoding="utf-8")
        time.sleep(0.3)
    speeds = speed_lines(before)
    _st["stop"] = True
    c1, f1 = mem()
    print(f"RAM end commit={c1} free={f1} peak={_st['max_commit']} "
          f"min_free={_st['min_free']} samples={_st['samples']}", flush=True)
    HERE.joinpath(f"browsecomp-hard-{label}.json").write_text(
        json.dumps({"label": label, "date": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "max_turns": MAX_TURNS,
                    "ram": {"start": [c0, f0], "end": [c1, f1],
                            "peak_commit": _st["max_commit"], "min_free": _st["min_free"]},
                    "speed_lines": speeds, "results": results}, indent=2), encoding="utf-8")
    print("=== speed lines ===", flush=True)
    for s in speeds[-14:]:
        print(s[:230], flush=True)
    print("DONE " + label, flush=True)
