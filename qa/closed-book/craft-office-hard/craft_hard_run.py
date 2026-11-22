"""Run the hard CraftSuite document task through Goose+Qwen, then score the docx."""
import ctypes
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import os

# DEPRECATED: this runner targeted Goose, which is no longer required or
# installed. Kept for reference only. Use a tool-capable harness as described
# in ../README.md. All tool paths come from the environment.
HERE = Path(__file__).resolve().parent
GOOSE = os.environ.get("HARNESS_GOOSE_EXE", "goose")
provider = sys.argv[1] if len(sys.argv) > 1 else "qwen_local_64k"
label = sys.argv[2] if len(sys.argv) > 2 else "qwen"
server_log = Path(sys.argv[3]) if len(sys.argv) > 3 else HERE / "server.log"
TASK = (HERE / "craft_doc_task.md").read_text(encoding="utf-8")
RESULT = HERE / "craft-hard-result.docx"

env = os.environ.copy()
env.update({
    "GOOSE_PROVIDER": provider, "GOOSE_TELEMETRY_ENABLED": "false",
    "GOOSE_MODE": "auto", "GOOSE_DISABLE_SESSION_NAMING": "true",
    "GOOSE_RANDOM_THINKING_MESSAGES": "false", "PYTHONIOENCODING": "utf-8",
})

class M(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
def mem():
    m=M(); m.dwLength=ctypes.sizeof(M); ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return (round((m.ullTotalPageFile-m.ullAvailPageFile)/2**30,1), round(m.ullAvailPhys/2**30,1))
_st={"max":0.0,"minfree":999.0,"stop":False}
def sampler():
    while not _st["stop"]:
        c,f=mem(); _st["max"]=max(_st["max"],c); _st["minfree"]=min(_st["minfree"],f); time.sleep(3)
threading.Thread(target=sampler,daemon=True).start()

def loglen():
    try: return len(server_log.read_text(encoding="utf-8",errors="replace").splitlines())
    except Exception: return 0

if __name__ == "__main__":
    if RESULT.exists(): RESULT.unlink()
    before=loglen(); c0,f0=mem()
    print(f"RUN craft-hard {label} RAM start commit={c0} free={f0}",flush=True)
    maxturns = sys.argv[4] if len(sys.argv) > 4 else "80"
    noprof = "--no-profile" in sys.argv
    cmd=[GOOSE,"run","--no-session","--output-format","json","--max-turns",maxturns]
    if noprof: cmd.append("--no-profile")
    cmd += ["--system","You are a document assistant. Use ONLY the WordCraft MCP tools to build the document exactly as asked. Do NOT use the shell. Actually call the WordCraft tools and save the file.","-t",TASK]
    t0=time.time()
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,encoding="utf-8",errors="replace",env=env,timeout=900)
        out,err,rc=p.stdout or "",p.stderr or "",p.returncode
    except subprocess.TimeoutExpired:
        out,err,rc="","","TIMEOUT"
    elapsed=round(time.time()-t0,1)
    (HERE/f"craft-hard-{label}-goose.txt").write_text(out+"\n=== STDERR ===\n"+err,encoding="utf-8")
    # tool calls + final text
    tools=[]; final=""
    try:
        s=out[out.index("{"):]; d=json.loads(s)
        for m in d.get("messages",[]):
            if m.get("role")=="assistant":
                for c in m.get("content",[]):
                    if c.get("type")=="toolRequest": tools.append(c.get("toolCall",{}).get("value",{}).get("name"))
                    elif c.get("type")=="text": final=c.get("text","")
        meta=d.get("metadata")
    except Exception as e:
        meta={"error":str(e)}; final=out[-500:]
    print(f"Goose finished rc={rc} in {elapsed}s, {len(tools)} tool calls",flush=True)
    print("tools:",tools,flush=True)
    print("final:",final[-400:],flush=True)

    # score the docx
    if RESULT.exists():
        sp=subprocess.run([sys.executable,str(HERE/"craft_score.py"),str(RESULT)],
                          capture_output=True,text=True,encoding="utf-8",errors="replace")
        score_out=sp.stdout
    else:
        score_out="SCORE 0/14 (no docx produced)"
    (HERE/f"craft-hard-{label}-score.txt").write_text(score_out,encoding="utf-8")
    print("\n=== SCORE ===",flush=True)
    print(score_out,flush=True)

    _st["stop"]=True; c1,f1=mem()
    print(f"RAM end commit={c1} free={f1} peak={_st['max']} minfree={_st['minfree']}",flush=True)
    print("metadata:",meta,flush=True)
    print("DONE",flush=True)
