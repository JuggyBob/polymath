# Mellum2.1-Instruct campaign — measured, with caveats

Dates: 2026-11-25 to 2026-11-26. All numbers below are from runs performed on
the author's machine. **This is not an official benchmark and nothing here is a
published benchmark result.** A row that did not complete is marked `NOT RUN`,
`CAPPED` or `INVALID` and is not estimated. Mellum2.1-Instruct did **not** beat
Qwen3.6 overall on any multi-contract repair suite.

## Setup and provenance

| Item | Value |
| --- | --- |
| Model | Mellum2.1-12B-A2.5B-Instruct — 12B total / 2.5B active MoE |
| Quant | MTP-Q4_K_M |
| Model file | 8,379,165,888 bytes; SHA-256 `c40903ca…5b6e10483de31`, locally verified against the upstream LFS object ID (**vendor-published** value) |
| Engine | llama.cpp b12728, Windows Vulkan build; target gfx1102, 16 GB GPU |
| Server flags | `-ngl 99`, `-ctk q8_0`, `-ctv q8_0`, `-cram 0`, `--spec-type draft-mtp`, `--spec-draft-n-max 1`; mmap left enabled |
| Context | 8,192 for the first single-request test; 65,536 (64K) for the repair campaigns |
| Interface | OpenAI-compatible server; dedicated harness profile, daily-driver config unchanged |
| Sampling | v4/v6 did not set sampling explicitly in the harness profile, so the exact harness values are unknown; v5 ran after the server was reverted to no explicit sampling flags |
| MTP acceptance | **Vendor-reported:** about 90%. **Measured:** ~0.9 mean across campaigns (0.87–0.90 per fixture), mean drafted length ~1.9 |

## First server test — single request, 8,192 context (2026-11-25)

Read-only preflight, then one non-streaming chat request on a simple code task
(a short Python function with a docstring). No process was killed or stopped;
unrelated resident applications were observed and left untouched.

**Measured:**

| Metric | Result |
| --- | ---: |
| HTTP status / finish reason | 200 / `stop` |
| Total time | 3.36 s |
| Prompt / completion tokens | 32 / 118 |
| Decode | **104.30 tok/s** (predicted_ms 1121.81) |
| Prefill | 14.34 tok/s (2231.41 ms for 32 tokens) |
| `reasoning_content` | empty — direct-answer checkpoint |
| Answer | correct and complete, 409 chars |
| MTP drafts | draft_n 59, accepted 58 → **98.3%** acceptance, mean drafted length 1.98 |
| Graphs | 59 reused, 0 reallocations |

Caveat: 104.30 tok/s is one short request. Under sustained agentic tool traffic
the realistic rate is ~92 tok/s (see the first v4 Python run below).

**Memory after load (measured, read-only):**

| Metric | Before | After |
| --- | ---: | ---: |
| Free physical | 15.83 GiB | 7.95 GiB |
| Commit used / limit | 20.66 / 50.11 GiB (41.2%) | 28.90 / 50.11 GiB (57.7%) |
| Free commit | 29.46 GiB | 21.21 GiB |
| Server private bytes | — | 8.39 GiB |
| Server working set | — | 7.94 GiB |
| GPU adapter dedicated | 1.36 GiB | 9.37 GiB |

VRAM fits with about 6 GiB headroom on the 16 GB card. The server's private
commit charge (~8.39 GiB) is far below the 36.8 GiB pinned arena measured for
the other local engine. Free physical RAM fell below the 12 GiB guard threshold
after load because the model's mmap'd working set competes with other resident
applications. Those pages are file-backed and reclaimable; the guard wrapper was
deliberately not used, and no auto-kill wrapper was started.

## Repair campaigns

Same fixtures, prompts, harness flags and scorers as the Qwen3.6-35B-A3B runs of
2026-11-19/20. Fresh candidate copies; published fixtures and scorers untouched.
Patched scorer copies were used only for a stale compiler path and an extended
timeout. One model was loaded at a time.

### v4 — full campaign (2026-11-25), PASSED

| Fixture | Visible | Hidden | Mellum total | Qwen total | Mellum wall | Qwen wall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Python | 28/28 | 21/42 | 49/70 | 64/70 | 93.0 s | 134.9 s |
| C++ | 29/29 | 25/41 | 54/70 | 69/70 | 159.9 s | 322.8 s |
| JavaScript | 28/28 | 28/40 | 56/68 | 66/68 | 99.8 s | 98.5 s |
| Rust | 28/28 | 32/40 | 60/68 | 68/68 | ~122.9 s* | 159.7 s |

\* Rust wall clock was derived from candidate-directory creation to output write;
the runner hit a scorer error before writing its timing line. All four harness
processes exited 0.

First v4 Python run detail (same fixture, measured): wall 92.97 s; decode
91.0–92.9 tok/s per request; prompt eval 368–710 tok/s uncached; MTP acceptance
0.88–1.00, mean drafted length ~1.9; 1500+ graphs reused, 0 reallocations.
Anti-cheat fields: `score_zero = false`, `regressions = []`,
`tests_modified/removed/added = []`, `files_removed = []`,
`public_api_intact = true`.

The hidden-test gap is capability, not tampering. Python's 21 hidden failures
include six that Qwen also failed, plus 15 more around cache invalidation,
pruning and window boundaries.

### v5 — default sampling after revert (2026-11-25/26)

| Fixture | Visible | Hidden | Mellum total | Qwen total | Mellum wall | Qwen wall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Python | NOT RUN | NOT RUN | NOT RUN | 76/80 | 1,894 s | 161.7 s |
| C++ | 16/16 | 27/49 | 43/65 | 63/65 | 2,123 s | ~300 s |
| JavaScript | 12/12 | 12/46 | 24/58 | 29/58 | 1,499 s | ~200 s |
| Rust | 24/24 | 24/45 | 48/69 | 69/69 | 151 s | 285.9 s |

Python v5 is **NOT RUN**: the published scorer's 300 s window returned `TIMEOUT`
(return code 124) and a patched copy with a 900 s window also returned
`TIMEOUT`. The agent's summary claimed the fixes were complete, but the
resulting test suite hangs — a genuine regression, not a scorer limit. No
comparable score can be reported.

Process/validity notes: the first uncapped campaign was terminated by a one-hour
outer timeout, but its C++ and JavaScript child agents survived and completed;
those two results are valid. A capped rerun (900 s) hit the cap on all four
fixtures; those capped runs are `NOT RUN`, not scores. A stale Rust agent left by
the capped run was stopped before the final retry. Python and Rust were then
rerun with a 3,600 s cap; both completed the agent phase, with Python's scorer
timing out as described. Only campaign-owned processes were stopped; unrelated
resident applications and the daily driver were untouched.

### v6 — spec-free, agent sees only `task/` (2026-11-25), PASSED

| Fixture | Visible | Hidden | Mellum total | Qwen total | Mellum perf | Qwen perf | Mellum wall | Qwen wall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Python | 28/79 | 1/29 | 29/108 | 108/108 | 1/3 | 1/3 | 123.0 s | 876.7 s |
| C++ | 35/35 | 2/29 | 37/64 | 64/64 | 0/2 | 0/2 | 67.9 s | 1,340.8 s |
| JavaScript | 39/39 | 11/34 | 50/73 | 42/73 | 0/4 | 4/4 | 100.5 s | 528.5 s |
| Rust | 12/12 | 3/26 | 15/38 | 27/38 | 2/4 | 2/4 | 137.3 s | 1,096 s |

All harness and scorer exits were 0, `score_zero = false`, no regressions, no
test edits. Findings:

- Python collapsed: the agent fixed one narrow README symptom in a single module
  and stopped. 51 visible and 28 hidden tests still failed — a task-comprehension
  failure, not an engine or scorer failure.
- C++ passed all 35 visible tests but only 2/29 hidden.
- JavaScript is the single correctness win (50/73 vs 42/73, 39/39 visible vs
  35/39), but Mellum failed all four performance checks while Qwen passed all
  four. This is not an overall win.
- Rust matched Qwen on visible tests (12/12) but found 3/26 hidden vs Qwen's 15/26.
- Wall clock was 5–20× shorter than Qwen across the suite, largely because Qwen
  did far more work per run. It is not a like-for-like throughput win.

## Speed recorded from the server (measured)

Decode stays in the ~88–97 tok/s band across languages and campaigns; draft
acceptance is ~0.9 throughout, consistent rather than a one-off.

| Campaign | Fixture | Requests | Decode mean (min–max) tok/s | Prefill mean tok/s | MTP acceptance (mean) |
| --- | --- | ---: | ---: | ---: | ---: |
| v4 | Python | 68 | 92.7 (81.3–104.1) | 631.1 | 0.89 |
| v4 | C++ | 38 | 91.5 (83.5–102.1) | 491.6 | 0.90 |
| v4 | JavaScript | 23 | 97.1 (88.0–103.3) | 682.5 | 0.90 |
| v4 | Rust | 29 | 93.5 (80.4–103.4) | 612.5 | 0.90 |
| v5 | Python | 74 | 87.6 | 892.3 | 0.90 |
| v5 | C++ | 81 | 90.9 | 1092.3 | 0.90 |
| v5 | JavaScript | 68 | 93.7 | 1120.0 | 0.90 |
| v5 | Rust | 23 | 91.7 | 596.2 | 0.90 |
| v6 | Python | 34 | 92.7 (81.3–104.1) | 631.1 | 0.89 |
| v6 | C++ | 14 | 96.7 (89.9–103.2) | 740.2 | 0.89 |
| v6 | JavaScript | 21 | 93.6 (82.8–102.2) | 700.2 | 0.89 |
| v6 | Rust | 26 | 88.7 (77.2–103.9) | 649.2 | 0.87 |

## INVALID experiment — v6 official-sampling rerun (2026-11-25/26)

Kept for completeness only. **This is not a valid sampling A/B and its score must
not be cited as a sampling result.**

Vendor-reported: the official quickstart sampling is `temperature=0.6`,
`top_p=0.95`, `top_k=20`; the supplied generation config has no sampling values
and no `min_p` guidance. The v4/v6 campaigns had not set sampling in the harness
profile, so their exact harness values are unknown. The server was restarted
with those explicit sampling parameters after a 90 s cooldown (only the
campaign's own server was stopped), and the exact v6 Python prompt was rerun on a
fresh candidate copy.

| Run | Score | `score_zero` | Regressions | Wall clock |
| --- | ---: | --- | ---: | ---: |
| v6 default sampling | 29/108 | false | 0 | 123.0 s |
| v6 official sampling — **INVALID** | 0/106 | true | 21 | 4,983.9 s |
| Qwen3.6 reference | 108/108 | false | 0 | 876.7 s |

Server-side speed during the invalid run: 181 requests, decode mean 86.2 tok/s
(21.9–102.7), prefill mean 874.3 tok/s, draft acceptance ~0.9. The candidate
ended with a broken parser and 21 example/roundtrip regressions.

**Why it is invalid:** three agents were running the same v6 Python prompt
concurrently on the **same candidate directory** for roughly the first 11
minutes. Two were stale processes left by failed launch attempts. They were
stopped with explicit approval; the intended run was left alone. The 0/106
result therefore cannot be attributed to the sampling parameters — concurrent
edits likely corrupted the workspace before the surviving agent finished.

**Decision:** per the rule "if it is not better, revert", the server was
restarted back to its original flags with no explicit sampling after another
90 s cooldown. The v5 campaign ran on that reverted server. No daily-driver
config or unrelated process was touched.

## Passed / Failed / NOT RUN

**Passed (valid measurements):**

- First single-request server test at 8,192 context, including the memory table.
- v4: all four languages scored; Python detail and anti-cheat fields clean.
- v5: C++, JavaScript and Rust scored; server speed measured for all four.
- v6: all four languages scored; perf checks and speed measured.
- Anti-cheat clean on every completed run: `score_zero = false`, no regressions,
  no test modifications/removals/additions, no files removed,
  `public_api_intact = true`.

**Failed (model performance on the fixtures, not infrastructure):**

- v4: 21/42, 25/41, 28/40 and 32/40 hidden tests passed (Python, C++, JS, Rust);
  Qwen passed more on every fixture.
- v5: 27/49, 12/46 and 24/45 hidden tests passed (C++, JS, Rust); Qwen passed
  more on every scored fixture.
- v6: 1/29, 2/29, 11/34 and 3/26 hidden tests passed; the JS correctness win was
  offset by 0/4 vs Qwen's 4/4 performance checks.
- v5 Python produced a hanging test suite — a genuine regression.

**NOT RUN / INVALID:**

- v5 Python: no comparable score (scorer timeouts at 300 s and 900 s).
- v5 capped rerun (900 s): all four fixtures `NOT RUN`, not scores.
- v6 official-sampling A/B: **INVALID** (concurrent stale agents on one
  workspace); not a score and not evidence about sampling.
- v7 on Mellum: `NOT RUN` — not attempted.
- No official benchmark submission was made.

## Caveats and limits

- Every number is from a single run on one machine and one GPU. No repeat-seed
  averages, confidence intervals or error bars.
- Wall-clock comparisons are not like-for-like: Qwen generally did substantially
  more work per run. Shorter wall time does not mean a better model.
- Context differed between the first test (8,192) and the repair campaigns
  (65,536); speeds are not adjusted for that difference.
- v4/v6 harness sampling values are unknown; v5 used reverted default sampling.
- Scorer copies were patched for a stale compiler path and a longer timeout;
  published fixtures and scorers were not modified. One v4 Rust wall time is
  derived, not directly measured.
- Absolute throughput is machine-specific. The 8,192-context decode figure comes
  from a single short request; sustained agentic decode is ~92 tok/s.
- Vendor-reported values (~90% MTP acceptance, quickstart sampling, model object
  ID) are labeled as such; all other numbers are locally measured.
- This is not an official benchmark. No claim is made that Mellum2.1-Instruct
  replaces Qwen3.6 as the daily coding driver.

## Verdict

Mellum2.1-Instruct is a fast worker/sub-agent: ~88–97 tok/s decode with ~0.9 MTP
draft acceptance, often much shorter wall clock on simple failures. It passed
fewer hidden tests than Qwen3.6 on every multi-contract repair suite here, and on
the spec-free v6 suite it was decisively weaker on three of four languages. The
one JavaScript correctness win carried a performance regression. It is not a
like-for-like replacement for the daily Qwen driver on careful repair work.
