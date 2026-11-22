# LFM2.5-24B-A2B via Hermes CLI — evaluation (2026-11-16)

Model: `<MODELS>\LFM2.5\LFM2.5-24B-A2B-UD-Q3_K_XL.gguf` (SHA-256 verified).
Server: `<TOOLS>\PolyStrata\strata-lfm25-ud-q3_k_m-64k.json`,
**64K context**, port 8081, HIP/gfx1102, thinking off.
Harness: **Hermes Agent CLI v0.23.1**, `-m lfm -z`, one session per question.
Question wording and answer keys are byte-identical to the Qwen runs.

## Scores vs Qwen3.6 (same questions, 32K, thinking off)

| Suite | LFM2.5 + Hermes | Qwen3.6 (earlier) |
| --- | ---: | ---: |
| Repair fixture (visible + hidden) | **15/18** (10/10 + 5/8) | 18/18 (10/10 + 8/8) |
| Easy mixed (12) | **9/12** | 12/12 |
| Hard general (20) | **16/20** | 20/20 |

### Easy mixed, by category

| Category | LFM | Qwen |
| --- | ---: | ---: |
| SWE-style | 3/3 | 3/3 |
| GPQA-style | 2/3 | 3/3 |
| AIME-style | 1/3 | 3/3 |
| MMLU-style | 3/3 | 3/3 |

LFM misses: CH3+ hybridization (answered C, wanted B), divisibility count (83 vs 125),
7^2024 mod 100 (81 vs 1).

### Hard set, by category

| Category | LFM | Qwen |
| --- | ---: | ---: |
| Code semantics | 3/5 | 5/5 |
| Science | 5/5 | 5/5 |
| Math | 3/5 | 5/5 |
| Knowledge | 5/5 | 5/5 |

LFM misses: closure late-binding (B vs C), dict insertion order (C vs D),
divisible-by-exactly-two count (133 vs 2333), 3^1000 mod 7 (2 vs 4).

## Repair fixture detail

LFM changed `inventory/store.py` and `inventory/report.py`:

- Off-by-one page index: **fixed correctly** (`start = (page-1)*size`).
- Unicode search: wrote `query.lower() in item.name.lower()` — Python `lower()`
  does not expand `ß → ss`, so `test_unicode_casefold` failed. Contract required
  `casefold()`. Qwen used `casefold()`.
- Exact cents total: summed `item.price_cents` instead of `item.value_cents`,
  ignoring quantity — `test_large_exact_sum` and `test_quantity_matters` failed.
  Qwen used `value_cents`.

No tests were modified; files changed were the two implementation modules.

## Speeds (engine-timed, from the server log, 81 requests)

| Metric | Median | Range |
| --- | ---: | --- |
| Decode | **90.0 tok/s** | 65.4 – 130.3 |
| Prefill (all requests, includes cache-reuse rows) | 726.3 tok/s | 145.4 – 1,586.8 |
| Prompt size | 12,356 tokens | 10,747 – 19,589 |

Fresh-read highlights:
- One-word probe: 12,204 tokens read at **1,533.9 tok/s**, 5 generated at 98.7.
- Full 12,204-token Hermes prompt read in 7,956 ms.
- Where the conversation cache reused 10,240 tokens, only ~2,000 new tokens
  were read at ~1,135 tok/s.
- Some replies used PolyStrata's repeat-text guessing (`drafts accepted 2 of 3`,
  `7 of 7`) even though the model has no MTP draft head.

**VRAM:** 2,432 of 2,432 routed experts in VRAM (9.5 GiB) — full residency,
no CPU expert fetches. No memory faults or paging during the run.

## Hermes client overhead

12,204 input tokens for a one-word prompt, versus Qwen Code desktop's 12,643.
So Hermes is **not** the lean client I speculated it might be.

## Caveats

- Hand-written question sets, not official benchmarks; 12/20 items cannot
  separate a 90% model from a 100% model.
- One Hermes session per question (fresh process each time); wall time per
  question 3.7–16.7 s including client startup.
- LFM ran at 64K, Qwen at 32K — different context settings, though the
  measured decode here does not show a 64K penalty.
- Thinking was off for both, per the earlier fix.
