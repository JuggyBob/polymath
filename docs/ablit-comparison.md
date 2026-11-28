# Abliterated vs base Qwen3.6-35B-A3B — sanitized comparison (research draft)

Compiled 2026-11-28 from local reports dated 2026-11-24 and 2026-11-25.

**Not an official benchmark.** Every number below comes from local, single-machine agentic repair runs on small fixture suites. Nothing here is a published benchmark result. No score is estimated for a run that did not complete: such rows are marked `NOT RUN` or `CAPPED`. Specific hidden-test identifiers and task-prompt text are deliberately withheld; only counts and totals are reported. Paths, account names, session and process identifiers, port numbers and key-file locations have been removed.

Conventions: **A** = abliterated model; **B** = base Qwen measured under matched conditions; **Q** = historical daily-Qwen reference, not a same-night A/B; `NOT RUN` = no stored score exists; `CAPPED` = harness time limit reached.

## Conditions (stated in the reports)

- **Model:** Qwen3.6-35B-A3B. A is the abliterated (refusal-direction ablated) variant; B is the daily-driver base model. Both are quantised. A is a GGUF Q3_K_M (heretic, native MTP preserved), 17,267,455,136 bytes, SHA-256 `7ea3bec5b190a340847b1c98a5b80a8e1a51b11cee0bedfe140caffcaa11b2ab`. B is its own UD-Q3_K_M quant, read-only. Abliteration is the main systematic difference between the two.
- **Context:** 98,304 tokens.
- **Engine:** pinned engine build `7a6c098…`; HIP, GPU 0; `--kv-whole`, `--conversation-cache-mib 0`, `--tail-skip 6`, `--cache-bias 0.25`, `--vram-reserve-mib 2000`.
- **Harness:** an OpenAI-compatible server plus an agent runner invoked with `--yolo --reasoning none`. Trial configs set `reasoning_effort: none`. Usage data reported `reasoning_tokens: 0` for seven of the eight matched-v7 runs (A C++ omitted the field) and compression telemetry reported `reasoning_items_pruned: 0` throughout. This was checked after the fact: thinking was off in both campaigns, so the v7 gaps are not a thinking-level mismatch.
- **Guard thresholds:** 80% commit ceiling, 65% start ceiling, 12 GiB free-physical floor; preflight ≥12 GiB free physical; ≥90 s cooldown between fixtures; one model loaded at a time. No threshold was lowered and no other agent's processes were touched. One Rust launch waited ~8 minutes for memory to free after another agent's emulator/Gradle work consumed it.
- **Isolation:** a trial directory held separate configs, expert-profile copies, agent-home overlays, run directories, usage/summary/score JSON and engine log excerpts. The daily-driver config, engine, expert profile, tokenizer and agent config were never modified.
- **Time limits:** A's first v7 pass used a 3,600 s (60 min) limit; the matched B rerun used 7,200 s (120 min).

## Verdict at a glance

| Suite | A | Reference | Delta | Reading |
|---|---:|---:|---:|---|
| v5 Python (run earlier) | 77/80 | Q 76/80 | +1 | A ahead |
| v5 C++ | 63/65 | Q 63/65 | 0 | tied |
| v5 Rust | 67/69 | Q 67/69 | 0 | tied |
| v5 JS | 58/58 | Q 29/58 | +29 | A ahead (reference later revised, see below) |
| v6 Python correctness | 108/108 | Q 108/108 | 0 | tied; perf 1/3 both |
| v6 C++ correctness | 64/64 | Q 64/64 | 0 | tied; perf 0/2 both |
| v6 Rust correctness | 20/38 | Q 27/38 | −7 | A behind; perf 2/4 both |
| v6 JS correctness | 50/73 | Q 42/73 | +8 | A ahead on correctness; perf 2/4 vs 4/4 |
| v7 Python correctness | 92/94 | Q 92/94, B 92/94 | 0 | tied; perf 2/6 both in the matched rerun |
| v7 C++ correctness | 67/94 | B 88/94 | −21 | A clearly behind; perf 0/6 both |
| v7 Rust correctness | 44/94 | B 93/94 | −49 | A clearly behind; A run capped; perf 4/6 both |
| v7 JS correctness | 54/94 | B 94/94 | −40 | A clearly behind; perf 4/6 vs 6/6 |

Aggregates as stated in the reports: v5 A **265/294 (90.1%)** vs Q **235/294 (79.9%)**; v6 A **242/283 (85.5%)** vs Q **241/283 (85.2%)**. **Unconfirmed:** the v5 denominator of 294 does not equal the sum of the four listed v5 fixture totals (80 + 65 + 69 + 58 = 272); the report does not explain the difference, so the percentage should not be recomputed from the table above.

**Bottom line:** v5 positive, v6 tied, v7 clearly worse. A was **not promoted**; daily Qwen remained the default model.

## v5 suite — 2026-11-24 (Python fixture run earlier)

Verdict: A matches or beats the daily-Qwen baseline on every fixture measured.

| Fixture | A | Q reference | Difference |
|---|---:|---:|---:|
| Python (run earlier) | **77/80** (25/25 visible, 52/55 hidden) | 76/80 (25/25, 51/55) | **+1** |
| C++ | **63/65** (16/16 visible, 47/49 hidden) | 63/65 (16/16, 47/49) | 0 |
| Rust | **67/69** (24/24 visible, 43/45 hidden) | 67/69 (24/24, 43/45) | 0 |
| JS | **58/58** (12/12 visible, 46/46 hidden) | 29/58 (12/12, 17/46) | **+29** |

`score_zero=false`, no regressions, no test files modified, added or removed, public API intact in all four.

- **Passed:** all four A fixtures at or above the stored Q reference; all visible tests in all four; all 46 hidden JS tests (Q passed 17); all 29 hidden Python tests except three; all C++/Rust hidden counts identical to Q.
- **Failed:** A missed 3 hidden Python tests, 2 hidden C++ tests and 2 hidden Rust tests; Q missed 4 hidden Python tests, the same 2 C++ and 2 Rust tests, and 29 hidden JS tests. Identifiers withheld.
- **NOT RUN:** no A-versus-Q same-night A/B was run for v5; all Q figures are historical score files and earlier reports. No agentic coding benchmark (SWE-bench or tool-call delta) was run.

Engine-reported speed during the agent runs (per-request medians):

| Fixture | Requests | Prefill tok/s | Decode tok/s |
|---|---:|---:|---:|
| C++ | 68 | 243.4 | 50.8 |
| Rust | 34 | 278.2 | 52.4 |
| JS | 37 | 356.1 | 78.1 |

Real-fix verification: A changed 3 C++ source files, 1 Rust source file, 5 JS source files and 4 Python source files versus the pristine copy; visible test files were identical. Agent transcripts contained no matches for grader, hidden-test, scorer or run-script marker strings; hidden tests were injected only at grading time. Usage was real: Python 31 API calls / 902k input tokens, C++ 68 / 2.28M, Rust 34 / 906k, JS 37 / 977k, all with `failed: false` and `finish_reason=stop`.

**Fairness rerun, 2026-11-25:** base Qwen was rerun on the v5 JS fixture and scored **56/58** (44/46 hidden, missing two hidden async tests) against A's **58/58**. The earlier 29/58 reference was therefore anomalous or under-conditioned. This is the one measured advantage A retains on a short fixture.

## v6 suite — 2026-11-24

Verdict: mixed. A ties on Python/C++ correctness, loses on Rust, and wins JS correctness while losing two JS performance checks.

| Fixture | A correctness | Q correctness | A perf | Q perf |
|---|---:|---:|---:|---:|
| Python | **108/108** (79/79 visible, 29/29 hidden) | 108/108 | 1/3 | 1/3 |
| C++ | **64/64** (35/35, 29/29) | 64/64 | 0/2 | 0/2 |
| Rust | **20/38** (12/12, 8/26) | **27/38** (12/12, 15/26) | 2/4 | 2/4 |
| JS | **50/73** (39/39, 11/34) | 42/73 (35/39, 7/34) | **2/4** | **4/4** |

`score_zero=false`, no regressions, no test edits in any fixture. Aggregate correctness A **242/283 (85.5%)** vs Q **241/283 (85.2%)** — effectively tied, with different per-language profiles.

- **Passed:** Python 29/29 and C++ 29/29 hidden tests; JS correctness +8 over Q; all perf pass counts except the JS block; all visible tests.
- **Failed:** Rust 18 hidden failures versus Q's 11 (−7); JS 23 hidden failures versus Q's 27; JS perf 2/4 versus Q's 4/4. Python/C++ perf were 1/3 and 0/2 for both models. Identifiers withheld.
- **NOT RUN:** no same-night base-Qwen rerun; references are dated 2026-11-20 reports.

A performance medians (ms; limits were reported but are not restated here): Python visible `perf_vis_small` 1.00 (pass), hidden `perf_vm_dispatch` 234.58 (fail), hidden `perf_serialize` 1800.31 (fail); C++ hidden `perf_disasm` 89.61 (fail), `perf_vars` 173.00 (fail); Rust visible `vis_print` 0.60 and `vis_disasm` 0.38 (both pass), hidden `perf_print` 73.02 and `perf_disasm` 34.33 (both fail); JS visible `perf_v_serialize` 0.42 (pass) and `perf_v_sumrange` 60.15 (fail), hidden `perf_serialize` 0.24 (pass) and `perf_sumrange` 134.94 (fail).

Real edits versus pristine: Python 8 files, C++ 8, Rust 4, JS 2; visible tests unchanged. Engine speed during the agent runs: Python 81 requests, prefill 266.6 / decode 59.6 tok/s; C++ 101, 288.3 / 62.5; Rust 98, 292.5 / 80.5; JS 47, 314.9 / 79.2.

## v7 suite — 2026-11-25

Verdict: the weakest showing. A matches base on Python correctness but is far worse on C++/Rust/JS.

### First A pass and stored references

| Fixture | A correctness | Q reference | A perf | Q ref perf |
|---|---:|---:|---:|---:|
| Python | **92/94** (45/45 visible, 47/49 hidden) | 92/94 (45/45, 47/49) | 2/6 | 6/6 |
| C++ | **67/94** (37/45, 30/49) | `NOT RUN` | 0/6 | `NOT RUN` |
| Rust | **44/94** (22/45, 22/49) — hermes hard timeout | `NOT RUN` | 4/6 | `NOT RUN` |
| JS | **54/94** (27/45, 27/49) — `score_zero=true` | `NOT RUN` | 4/6 | `NOT RUN` |

Only Python had a stored Q v7 score. A failed 2 hidden Python tests and Q failed 2 (different identifiers withheld), with the same total; A had 4 fewer perf passes. In the matched rerun below, measured B Python perf was also 2/6, so the 6/6 figure is a historical reference, not a matched result.

- **Passed:** A Python correctness tied at 92/94; A made real source edits in all four fixtures (8/8/8/6 files), with no test edits, no regressions and public API intact.
- **Failed:** A C++ 67/94, Rust 44/94, JS 54/94; A Python perf 2/6; A C++ perf 0/6.
- **NOT RUN / CAPPED:** Q v7 references for C++, Rust and JS did not exist on disk and were not fabricated. A Rust hit a 3,600 s hermes hard limit (`HERMES_HARD_TIMEOUT`, elapsed 3,613.6 s); the scorer still scored the partial workspace, so 44/94 is partial work and must not be compared as a clean completion.

Important scorer detail: `score_zero=true` on A JS is set by this fixture's scorer whenever **any** hidden test fails; it is not a tampering verdict. All tampering fields (`tests_modified`, `tests_removed`, `tests_added`, `files_removed`, `regressions`) were empty. The 22 hidden failures are counted above; identifiers are withheld.

### Matched A/B rerun — 2026-11-25 (decisive)

Base Qwen was rerun on all four v7 fixtures under the same conditions as A except for the longer 7,200 s limit, a separate trial server, a base config and a base agent-home overlay. Both C++ and JS A runs completed normally (1,311.6 s and 2,034.7 s; about 21.9 and 33.9 min), so those gaps are not timeout artifacts. Only A Rust was cut short.

| Fixture | A correctness | B correctness | Difference | A perf | B perf |
|---|---:|---:|---:|---:|---:|
| Python | 92/94 (45, 47) | 92/94 (45, 47) | tied | 2/6 | 2/6 |
| C++ | 67/94 (37, 30) | **88/94** (45, 43) | **B +21** | 0/6 | 0/6 |
| Rust | 44/94 (22, 22) — capped | **93/94** (45, 48) | **B +49** | 4/6 | 4/6 |
| JS | 54/94 (27, 27) | **94/94 (perfect)** (45, 49) | **B +40** | 4/6 | **6/6** |

- **Passed:** A tied B on Python; all four B runs completed; both models made genuine source edits (A 8/8/8/6 files; B 7/9/9/10 files), with no test edits, no regressions and no public-API violations.
- **Failed:** A lost 21, 49 and 40 correctness points on C++, Rust and JS, and lost the JS perf block 4/6 vs 6/6. A JS hit its 500-call API budget; B used 138 calls. More calls did not help A.
- **NOT RUN:** none in the matched set; the earlier stored Q references for C++/Rust/JS remain `NOT RUN`.

Elapsed and API calls (A vs B): Python 1,861.9 s / 244 vs 1,601.4 s / 187; C++ 1,311.6 s / 120 vs 2,414.8 s / 195 (B spent about 18 min longer and fixed 21 more hidden tests); Rust 3,613.6 s (capped, partial work) vs 1,669.1 s / 212 (B finished in less than half the time with 48/49 hidden passing); JS 2,034.7 s / 500 (budget hit) vs 1,269.1 s / 138.

Hidden-failure counts, A vs B (identifiers withheld): Python 2 vs 2; C++ 19 vs 6 (B's set was a strict subset of A's); Rust 27 vs 1; JS 22 vs 0.

Perf medians (ms, A vs B) are reported only where they help interpret the gap. Python: visible `perf_print` 5289.96 / 4892.89 (both fail), `perf_disasm` 56.91 / 59.14 (both pass), `perf_snapshot` 2.85 / 2.98 (both fail); hidden `perf_print` 4779.15 / 4697.09 (fail), `perf_disasm` 60.43 / 59.64 (pass), `perf_snapshot` 2.81 / 2.85 (fail). C++: all 12 checks fail in both runs, so perf does not explain the correctness gap. Rust: visible `vis_print` 1.22 / 1.16, `vis_disasm` 2.25 / 2.17, `vis_snapshot` 0.04 / 0.03 (all pass); hidden `perf_print` 463.63 / 359.29 and `perf_disasm` 142.16 / 220.89 (both fail), `perf_snapshot` 0.33 / 0.30 (both pass). JS: visible `perf_print` 16.57 / 16.65 and `perf_disasm` 0.12 / 1.28 (both pass), `perf_snapshot` 1.08 / 1.62 (A fail, B pass); hidden `perf_print` 14.74 / 14.92 and `perf_disasm` 0.12 / 1.0 (both pass), `perf_snapshot` 0.57 / 2.95 (A fail, B pass).

## Refusal probe (separate from the repair fixtures)

A hard hypothetical probe of six serious fictional scenarios, capped at 800 tokens each:

| Model | Refusals |
|---|---:|
| A | **0/6** — answered all six in detail |
| B / daily Qwen | **5/6** — complied with one scenario |

An earlier, softer probe was A 0/6 vs Q 1/6. This is the measured benefit of the ablation. **Unconfirmed:** the verdict report attaches "31 API calls, 902k input tokens, `finish_reason=stop`" to this probe, but those same figures also appear as the v5 Python agent usage, so the association is ambiguous. Scenario content is withheld.

## Speed

Standalone engine benchmark on A (96K context): chat decode **83.7 tok/s**, TTFT **0.26 s**, 4K prefill **1147.3 tok/s**, 16K prefill **982.0 tok/s**, agent decode **76.0 tok/s**, cache hit **68.6%**. Historical daily-Qwen reference: **75.9 tok/s** sci-fi and **78.7 tok/s** mean over 121 agentic requests. These are different suites and methods, so the comparison is indicative only; **no speed penalty was observed**. During fixture runs, prefill ran 240–360 tok/s and decode 50–81 tok/s depending on request mix, with natural finishes and no forced token IDs.

## Caveats and limits

- One run per model per fixture in each campaign; no repeated-run variance estimate anywhere.
- v7 is spec-free, long-horizon and uses masked faults: a later fault only appears after an earlier one is fixed. Partial credit is expected, and scores are not comparable across suites with different test counts.
- Hidden totals differ by suite and language (v5 55/49/45/46 hidden; v6 29/29/26/34; v7 49/49 each), so raw totals must not be equated across languages.
- Q figures for v5 and v6 are historical dated files and reports, not same-night A/B runs. The v5 JS 29/58 reference was later shown to be anomalous (matched fairness rerun: Q 56/58).
- A Rust v7 is capped at 3,600 s; its 44/94 is partial work. A C++ and JS completed normally.
- Performance checks are noisy and machine-load dependent; v7 C++ failed all 12 checks in both runs, so those timings are not a discriminator. The v7 absolute 0/6 C++ perf result is partly a timing artifact of that machine/load.
- The v5 C++ fixture had a published scorer defect (`NameError: shutil`) worked around in a trial copy of the scorer only; the patch adds a missing import and does not change scoring logic. The published fixture was untouched.
- v5 and v6 base references were not rerun the same night. v7 is the only suite with a matched base rerun, and it is the decisive one.
- No SWE-bench or tool-call benchmark was run; these repair fixtures are small tasks and are not a full proxy for daily agent work.
- The abliterated GGUF is community-hosted rather than an official release; long-term availability is a concern (the verified file with the SHA-256 above should be archived).
- Inference, not measurement: the identical C++/Rust v5 failures are consistent with identical base weights in which only the refusal direction was ablated; this is an explanation, not a separately tested hypothesis.

## Recommendation

1. **Do not promote A to daily driver.** Under matched v7 conditions it is tied on Python but clearly worse on C++ (B +21), Rust (B +49) and JS (B +40), with the JS perf block also favouring B. The refusal benefit does not compensate for a regression of that size on agentic repair work.
2. **Keep the daily Qwen base model as default.** If less-refusal behaviour is wanted, use A as an opt-in second model or configuration, not the daily driver.
3. **Revisit only** if a future ablation method preserves v7 performance, or after repeated v7 runs on stronger hardware or a stronger quant. Neither is measured here.

## Artifacts (generic names only)

Source reports: v5 suite result, v6 suite result, v7 suite result, final verdict, matched v7 A/B report. Trial data: trial directory containing configs, prompts, expert-profile copies, agent-home overlays, campaign score JSONs, usage/summary JSONs, run directories, engine log excerpts and a patched scorer copy. Refusal probes: ablit/base hard and soft probe result files. Speed: a community benchmark readme in the trial results folder.
