# Qwen3.6-35B-A3B evaluation — 16 November 2026

Model: `qwen3.6-35b-a3b-ud-q3_k_m` on PolyStrata, optimized config (`--cache-bias 0.25`).
All tests ran against `http://127.0.0.1:8080/v1`. Server stopped after the run.

## 1. Repair fixture (the suite used for Qwen Code vs DSH on Flash-Next Coder)

Harness: Qwen Code CLI 0.27.x, one-shot `--yolo --channel CI`, fresh copy of
`<REPO>\repair\template` → `<REPO>\repair\qwen36`.
Scored with `score.py <dir> <hidden>`.

| | Qwen3.6 | Flash-Next Coder (earlier run) |
|---|---:|---:|
| Visible tests | **10/10** | 10/10 |
| Hidden tests | **8/8** | 8/8 |
| Tests modified | 0 | 0 |
| Files changed | `inventory/store.py`, `inventory/report.py` | same two files |

The model fixed the off-by-one page index, the missing query casefold, and the cents-rounding bug in one
pass; it correctly left the documented red herring alone. **18/18 — parity with the Coder model.**

## 2. Twelve-question mixed eval

Hand-written questions in the named styles — **not official benchmark items**. Fixed answer keys, temperature 0,
greedy, one `ANSWER:` line required. Full responses in `<REPO>\qa\closed-book\easy-mixed-12\qwen36-knowledge-eval.json`.

| Category | Score | Notes |
|---|---:|---|
| SWE-style (code reasoning) | 3/3 | even-sum function, dict mutation during iteration, dict lookup complexity |
| GPQA-style (graduate science) | 3/3 | weak neutral boson, CH3+ hybridization, Schwarzschild radius |
| AIME-style (competition math) | 3/3 | divisibility count, x+1/x identity, 7^2024 mod 100 |
| MMLU-style (broad knowledge) | 3/3 | shortest day, Westphalia, Python's creator |

**Total 12/12.** Decode during the reasoning answers averaged roughly 96–110 tok/s.

The reasoning traces were checked on the harder items — the AIME questions were solved by actual derivation
(Euler's totient for the modular exponent, algebraic identity for x²+1/x²), not guessing. Answers were emitted
in the exact requested format.

## Caveats

- A 12-question hand-written set is a smoke test, not a benchmark score. It cannot distinguish a 90% model
  from a 100% model; it only shows no obvious failure on these topics.
- The repair fixture is small (18 assertions) and was already solved by the Coder model. Parity there means
  Qwen3.6 did not regress on this particular task; it does not establish general coding equivalence.
- Only the Qwen Code harness was run today. The DSH harness was not re-run.
- Qwen Code settings were temporarily pointed at Qwen3.6 (32K context) and have been **restored** to the
  original Coder config (262144 context). The PolyStrata server is stopped and port 8080 is free.
