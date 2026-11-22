"""30 genuinely hard questions with hand-verified answer keys.

Subtle code semantics, graduate-level science, competition math and
non-trivial general knowledge. All answer keys were derived by hand.
These are NOT official benchmark items.

Expanded 2026-11-20 from 20 to 30 questions. The original 20-question run
is preserved in qwen36-hard-eval.json; this script writes
qwen36-hard-eval-30.json so old results are not overwritten and past
baselines remain reproducible.

Two items were also clarified in this expanded copy: the newly added
square-well third-excited-state item now states that the ground state is
n = 1, and one pre-existing item, the Rite of Spring distractor, no longer
contains Stravinsky's name. No other original item was changed.
The counting item originally added at this position was replaced with a harder
modular-arithmetic item (17^2024 mod 100 = 21) after review found it too close
to an easy-set item.
"""

import json
import re
import time
import urllib.request
from pathlib import Path

URL = "http://127.0.0.1:8080/v1/chat/completions"
OUT = Path(r"<REPO>\closed-qa\hard-mixed-20\qwen36-hard-eval-30.json")

Q = [
    # ---------------- subtle code semantics ----------------
    ("code", "C", """What is printed by this Python program?

def make():
    fs = []
    for i in range(3):
        fs.append(lambda: i)
    return fs
print([f() for f in make()])

A) [0, 1, 2]
B) [0, 0, 0]
C) [2, 2, 2]
D) [3, 3, 3]"""),

    ("code", "A", """What is printed?

class A:
    def f(self): return "A"
class B(A):
    def f(self): return "B" + super().f()
class C(A):
    def f(self): return "C" + super().f()
class D(B, C):
    def f(self): return "D" + super().f()
print(D().f())

A) DBCA
B) DBCA with an extra A
C) DABC
D) D followed by B only"""),

    ("code", "A", """This function counts set bits in a positive integer:

def f(n):
    c = 0
    while n:
        n &= n - 1
        c += 1
    return c

What does f(2024) return?
A) 7
B) 6
C) 8
D) 10"""),

    ("code", "B", """How many distinct calls to fib are actually executed (including the initial one) when fib(10) is called for the first time on a fresh cache?

import functools
@functools.lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n-1) + fib(n-2)

A) 10
B) 11
C) 177
D) 89"""),

    ("code", "D", """What is printed?

d = {}
for i in range(3):
    d[i] = i
del d[1]
d[1] = 99
print(list(d))

A) [0, 1, 2]
B) [0, 1]
C) [1, 0, 2]
D) [0, 2, 1]"""),

    # ---------------- graduate-level science ----------------
    ("science", "B", """A particle in a one-dimensional infinite square well of width L has ground-state energy E1. The well is widened to 2L without changing the particle. What is the new ground-state energy?

A) E1 / 2
B) E1 / 4
C) 2 E1
D) 4 E1"""),

    ("science", "C", """A buffer contains acetic acid (pKa = 4.76) and sodium acetate with [acetate]/[acid] = 10. What is the pH?

A) 3.76
B) 4.76
C) 5.76
D) 6.76"""),

    ("science", "A", """Approximately what is the Schwarzschild radius of the Earth? (M ≈ 5.97e24 kg, G ≈ 6.67e-11, c ≈ 3.00e8 m/s)

A) 9 mm
B) 9 cm
C) 9 m
D) 9 km"""),

    ("science", "B", """In a population at Hardy-Weinberg equilibrium, the recessive allele frequency is q = 0.1. What fraction of the population is heterozygous?

A) 0.01
B) 0.18
C) 0.81
D) 0.20"""),

    ("science", "D", """Which enzyme catalyzes the oxidative decarboxylation of isocitrate to alpha-ketoglutarate in the citric acid cycle?

A) Citrate synthase
B) Alpha-ketoglutarate dehydrogenase
C) Succinate dehydrogenase
D) Isocitrate dehydrogenase"""),

    # ---------------- competition math ----------------
    ("math", "2333", """How many positive integers n <= 10000 are divisible by exactly two of the numbers 2, 3, and 5? Reply with the integer."""),

    ("math", "4", """What is the remainder when 3^1000 is divided by 7? Reply with the integer."""),

    ("math", "126", """How many positive five-digit integers have their digits in strictly increasing order from left to right? Reply with the integer."""),

    ("math", "36/5", """A right triangle has legs of length 9 and 12. What is the length of the altitude from the right angle to the hypotenuse? Reply as a fraction like a/b."""),

    ("math", "8", """What is the smallest positive integer n such that 2^n is congruent to 1 modulo 17? Reply with the integer."""),

    # ---------------- non-trivial general knowledge ----------------
    ("knowledge", "B", """Who wrote 'The Structure of Scientific Revolutions', introducing the concept of paradigm shifts?
A) Karl Popper
B) Thomas Kuhn
C) Paul Feyerabend
D) Imre Lakatos"""),

    ("knowledge", "A", """The principle of non-refoulement, which forbids returning refugees to a country where they face serious harm, is a cornerstone of which instrument?
A) The 1951 Geneva Convention relating to the Status of Refugees
B) The Geneva Conventions of 1949 on the laws of war
C) The Universal Declaration of Human Rights
D) The Schengen Agreement"""),

    ("knowledge", "C", """Which enzyme catalyses the rate-limiting (committed) step of glycolysis?
A) Hexokinase
B) Glucokinase
C) Phosphofructokinase-1
D) Pyruvate kinase"""),

    ("knowledge", "D", """Who composed 'The Rite of Spring', the ballet that caused a riot at its 1913 premiere?
A) Claude Debussy
B) Arnold Schoenberg
C) Maurice Ravel
D) Igor Stravinsky"""),

    ("knowledge", "B", """Which amino acid is the biochemical precursor to both serotonin and melatonin?
A) Tyrosine
B) Tryptophan
C) Phenylalanine
D) Histidine"""),

    # --- added 2026-11-20: 10 more, total 30 ---
    # code
    ("code", "B", """What is printed?

def f(x, acc=[]):
    acc.append(x)
    return acc
print(f(1)); print(f(2)); print(f(3))

A) [1], [2], [3]
B) [1], [1, 2], [1, 2, 3]
C) [1], [1], [1]
D) TypeError"""),

    ("code", "B", """What is printed?

def f():
    try:
        return 1
    finally:
        return 2
print(f())

A) 1
B) 2
C) None
D) TypeError"""),

    ("code", "B", """What is printed by print(-7 // 3, -7 % 3)?
A) -2 -1
B) -3 2
C) -2 2
D) -3 -1"""),

    # science
    ("science", "B", """A charged particle moves in a uniform magnetic field with its velocity perpendicular to the field. Ignoring radiation, what happens to its kinetic energy?
A) It increases continuously
B) It stays constant
C) It decreases continuously
D) It oscillates at the cyclotron frequency"""),

    ("science", "B", """A particle in a one-dimensional infinite square well of width L has ground-state energy E1. What is the energy of its third excited state? (Take the ground state as n = 1.)
A) 9 E1
B) 16 E1
C) 4 E1
D) 25 E1"""),

    ("science", "A", """A uniform solid sphere rolls without slipping. What fraction of its total kinetic energy is rotational?
A) 2/7
B) 2/5
C) 5/7
D) 1/2"""),

    # math
    ("math", "21", """What is the remainder when 17^2024 is divided by 100? Reply with the integer."""),

    ("math", "38", """How many positive integers <= 1000 are perfect squares or perfect cubes (or both)? Reply with the integer."""),

    # knowledge
    ("knowledge", "A", """Which treaty, signed in 1987, eliminated an entire class of intermediate-range nuclear missiles?
A) INF Treaty
B) START I
C) SALT II
D) Treaty on the Non-Proliferation of Nuclear Weapons"""),

    ("knowledge", "A", """The 1968 Kerner Commission warned that the United States was moving toward what?
A) two societies, separate and unequal
B) a single melting pot
C) a permanent welfare state
D) a military dictatorship"""),
]


def ask(question):
    body = json.dumps({
        "messages": [
            {"role": "system", "content": "You are taking a difficult test. Follow the answer format exactly."},
            {"role": "user", "content": question + "\n\nReply with exactly one line: ANSWER: <letter-or-number-or-fraction>. No other text."},
        ],
        "temperature": 0,
        "max_tokens": 4096,
    }).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    start = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        resp = json.load(r)
    elapsed = time.time() - start
    msg = resp["choices"][0]["message"]
    text = (msg.get("content") or "") + "\n" + (msg.get("reasoning_content") or "")
    matches = re.findall(r"ANSWER:\s*([A-D]|\d+/\d+|\d+)", text, re.IGNORECASE)
    parsed = matches[-1].upper() if matches else ""
    return {
        "parsed": parsed,
        "content": msg.get("content"),
        "reasoning": msg.get("reasoning_content"),
        "timings": resp.get("timings"),
        "elapsed_s": round(elapsed, 2),
    }


results = []
for i, (cat, expected, question) in enumerate(Q):
    print(f"[{i+1:2d}/30] {cat:<9}", end=" ", flush=True)
    try:
        r = ask(question)
    except Exception as e:
        r = {"parsed": "", "error": str(e)}
    ok = r.get("parsed") == expected
    print(("OK  " if ok else "MISS") + f" got={r.get('parsed')!r} want={expected!r}", flush=True)
    results.append({"category": cat, "expected": expected, "question": question, "correct": ok, **r})
    time.sleep(0.3)

by_cat = {}
for cat in ("code", "science", "math", "knowledge"):
    rows = [r for r in results if r["category"] == cat]
    by_cat[cat] = {"correct": sum(r["correct"] for r in rows), "total": len(rows)}

report = {
    "model": "qwen3.6-35b-a3b-ud-q3_k_m (PolyStrata optimized, cache-bias 0.25)",
    "date": time.strftime("%Y-%m-%d %H:%M:%S"),
    "note": "Hard hand-written questions with hand-verified keys; not official benchmark items.",
    "by_category": by_cat,
    "total_correct": sum(v["correct"] for v in by_cat.values()),
    "total_questions": len(Q),
    "results": results,
}
OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
print("\n--- summary ---")
for cat, v in by_cat.items():
    print(f"{cat:<10} {v['correct']}/{v['total']}")
print(f"TOTAL      {report['total_correct']}/{report['total_questions']}")
print("saved:", OUT)
