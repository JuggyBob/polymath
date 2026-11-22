"""20-question mixed eval against the local PolyStrata server.

Hand-written questions in the style of SWE-bench debugging, GPQA, AIME and
MMLU. These are NOT official benchmark items; they are a repeatable local
check with fixed answer keys.

Expanded 2026-11-20 from 12 to 20 questions (two new per category). The
original 12-question run is preserved in qwen36-knowledge-eval.json; this
expanded script writes qwen36-knowledge-eval-20.json so old results are not
overwritten and past baselines remain reproducible.
"""

import json
import re
import time
import urllib.request
from pathlib import Path

URL = "http://127.0.0.1:8080/v1/chat/completions"
OUT = Path(r"<REPO>\closed-qa\easy-mixed-12\qwen36-knowledge-eval-20.json")

QUESTIONS = [
    # --- SWE-style ---
    ("swe", "B", """What does this function return when data = [1, 2, 3, 4]?

def f(data):
    total = 0
    for x in data:
        if x % 2 == 0:
            total += x
    return total

A) 4   B) 6   C) 10   D) 7"""),
    ("swe", "B", """This Python code fails with 'dictionary changed size during iteration':

d = {"a": 1, "b": 2}
for k in d:
    if d[k] == 2:
        del d[k]

Which single change fixes it?
A) for k in d.keys():
B) for k in list(d):
C) for k in d.items():
D) wrap del in try/except RuntimeError"""),
    ("swe", "A", """What is the average-case time complexity of looking up a key in a Python dict?
A) O(1)   B) O(log n)   C) O(n)   D) O(n log n)"""),

    # --- GPQA-style ---
    ("gpqa", "C", """Which gauge boson mediates the weak neutral current in the Standard Model?
A) photon   B) W+ boson   C) Z^0 boson   D) gluon"""),
    ("gpqa", "B", """What is the hybridization of the carbon atom in the methyl cation, CH3+?
A) sp   B) sp2   C) sp3   D) dsp2"""),
    ("gpqa", "B", """For a non-rotating, uncharged black hole of mass M, what is the Schwarzschild radius (event horizon)?
A) GM/c^2   B) 2GM/c^2   C) sqrt(2GM/c^2)   D) GM/(2c^2)"""),

    # --- AIME-style ---
    ("aime", "125", """How many positive integers n <= 1000 are divisible by 6 but NOT divisible by 8? Reply with the integer."""),
    ("aime", "7", """If x + 1/x = 3, what is x^2 + 1/x^2? Reply with the integer."""),
    ("aime", "1", """What is the remainder when 7^2024 is divided by 100? Reply with the integer."""),

    # --- MMLU-style ---
    ("mmlu", "B", """Which planet in our solar system has the shortest day (rotation period)?
A) Mercury   B) Jupiter   C) Venus   D) Earth"""),
    ("mmlu", "A", """The Treaty of Westphalia (1648) brought an end to which conflict?
A) Thirty Years' War   B) Hundred Years' War   C) Seven Years' War   D) War of the Spanish Succession"""),
    ("mmlu", "B", """Who designed the Python programming language?
A) Dennis Ritchie   B) Guido van Rossum   C) James Gosling   D) Brendan Eich"""),

    # --- added 2026-11-20: two more per category, total 20 ---
    ("swe", "A", """What does this return?

[x*x for x in range(5) if x % 2 == 1]

A) [1, 9]   B) [0, 4, 16]   C) [1, 3, 9]   D) [0, 1, 4, 9, 16]"""),

    ("swe", "A", """What is len(set([1, 2, 2, 3, 3, 3]))?
A) 3   B) 4   C) 6   D) 2"""),

    ("gpqa", "A", """Which of these particles is its own antiparticle?
A) photon   B) electron   C) proton   D) neutron"""),

    ("gpqa", "C", """With E1 = -13.6 eV for hydrogen, what is the energy of the n = 2 level?
A) -27.2 eV   B) -6.8 eV   C) -3.4 eV   D) -1.7 eV"""),

    ("aime", "56", """What is the sum of all positive divisors of 28? Reply with the integer."""),

    ("aime", "30", """How many two-digit positive integers are divisible by 3? Reply with the integer."""),

    ("mmlu", "B", """Which organelle is the main site of oxidative phosphorylation in eukaryotic cells?
A) nucleus   B) mitochondrion   C) ribosome   D) Golgi apparatus"""),

    ("mmlu", "A", """Which agreement established the World Trade Organization?
A) Marrakesh Agreement   B) GATT 1947   C) Bretton Woods Agreement   D) NAFTA"""),
]


def ask(question):
    body = json.dumps({
        "messages": [
            {"role": "system", "content": "You are taking a short test. Follow the answer format exactly."},
            {"role": "user", "content": question + "\n\nReply with exactly one line: ANSWER: <letter-or-integer>. No other text."},
        ],
        "temperature": 0,
        "max_tokens": 2048,
    }).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    start = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        resp = json.load(r)
    elapsed = time.time() - start
    msg = resp["choices"][0]["message"]
    text = (msg.get("content") or "") + "\n" + (msg.get("reasoning_content") or "")
    matches = re.findall(r"ANSWER:\s*([A-D]|\d+)", text, re.IGNORECASE)
    parsed = matches[-1].upper() if matches else ""
    if not parsed:
        plain = re.findall(r"(?:^|\s)([A-D]|\d+)(?:\s|[.)]|$)", msg.get("content") or "", re.MULTILINE)
        parsed = plain[0].upper() if plain else ""
    return {
        "parsed": parsed,
        "content": msg.get("content"),
        "reasoning": msg.get("reasoning_content"),
        "timings": resp.get("timings"),
        "elapsed_s": round(elapsed, 2),
    }


results = []
for i, (cat, expected, question) in enumerate(QUESTIONS):
    print(f"[{i+1:2d}/20] {cat} ...", end=" ", flush=True)
    try:
        r = ask(question)
    except Exception as e:
        r = {"parsed": "", "error": str(e)}
    ok = r.get("parsed") == expected
    print(("OK " if ok else "MISS") + f" got={r.get('parsed')!r} expected={expected!r}", flush=True)
    results.append({"category": cat, "expected": expected, "question": question, "correct": ok, **r})
    time.sleep(0.5)

by_cat = {}
for cat in ("swe", "gpqa", "aime", "mmlu"):
    rows = [r for r in results if r["category"] == cat]
    by_cat[cat] = {"correct": sum(r["correct"] for r in rows), "total": len(rows)}

report = {
    "model": "qwen3.6-35b-a3b-ud-q3_k_m (PolyStrata optimized, cache-bias 0.25)",
    "date": time.strftime("%Y-%m-%d %H:%M:%S"),
    "note": "Hand-written questions in these styles, not official benchmark items.",
    "by_category": by_cat,
    "total_correct": sum(v["correct"] for v in by_cat.values()),
    "total_questions": len(QUESTIONS),
    "results": results,
}
OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print("\n--- summary ---")
for cat, v in by_cat.items():
    print(f"{cat:<6} {v['correct']}/{v['total']}")
print(f"TOTAL  {report['total_correct']}/{report['total_questions']}")
print("saved:", OUT)
