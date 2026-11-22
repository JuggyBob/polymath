# Qwen3.6 hard eval — 20 questions

Model: `qwen3.6-35b-a3b-ud-q3_k_m` on PolyStrata with the optimized config (`--cache-bias 0.25`).
Full responses and keys: `<REPO>\qa\closed-book\hard-mixed-20\qwen36-hard-eval.json`. Server stopped after the run.

## Results

| Category | Score |
|---|---:|
| Subtle code semantics | 5/5 |
| Graduate-level science | 5/5 |
| Competition math | 5/5 |
| Non-trivial general knowledge | 5/5 |
| **TOTAL** | **20/20** |

## What the questions covered

**Code:** lambda late binding; diamond MRO with `super()`; popcount via `n &= n-1`; counting distinct `lru_cache` calls; dict reinsertion ordering.

**Science:** infinite-well energy scaling; Henderson–Hasselbalch; Earth's Schwarzschild radius from G, M, c; Hardy–Weinberg heterozygotes; TCA-cycle enzyme.

**Math:** inclusion–exclusion for numbers divisible by exactly two of 2/3/5; modular exponentiation; strictly-increasing five-digit numbers; altitude of a 9-12-15 triangle; multiplicative order of 2 mod 17.

**Knowledge:** Kuhn; non-refoulement; PFK-1; Stravinsky; tryptophan as serotonin/melatonin precursor.

All 20 answer keys were verified independently before the run (including a brute-force check of the 2333 count and a direct calculation of the 8.85 mm Schwarzschild radius).

## Parsing caveat

The initial parse scored 19/20: on the isocitrate question the model's **final content was `ANSWER: D`** (correct), but its reasoning echoed the instruction text `ANSWER: <letter-or-number-or-fraction>`, and the parser took the last regex match across content + reasoning — which landed on the echoed `A`. Scoring was redone using only the final `ANSWER:` line in the response content, giving 20/20. The model's reasoning on that item correctly identified isocitrate dehydrogenase and rejected all three alternatives.

## Interpretation

A perfect score on 20 hard questions is impressive, but this is still a **hand-written set, not an official benchmark**. It establishes that the model handles subtle Python semantics, multi-step math and graduate-level science without errors on these specific items. It does not prove a general capability level, and the questions are fixed — a model could in principle be overfit to them.

Combined with the earlier results: 18/18 repair fixture, 12/12 easier mixed set, 20/20 hard set, at ~85 tok/s sustained (peaks >100). On the evidence available, Qwen3.6-35B-A3B Q3_K is at least as capable as the 125B Coder on everything tested here.
