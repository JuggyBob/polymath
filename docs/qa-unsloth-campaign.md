# QA campaign — Qwen3.6-35B-A3B via Unsloth Desktop API (measured, with caveats)

Dates: 2026-11-20 for all four suites. Four separate single runs on the
author's machine. Nothing here is a published benchmark result, and no official
benchmark claim is made: every question set is hand-written and hand-keyed
locally, including the set called "BrowseComp-HARD". These are not official
BrowseComp items.

**Measured vs claimed.** A number labelled *measured* came from a run described
here. A number labelled *claimed* is from an earlier documented baseline on a
different transport; it was not re-measured and no per-item data from it was
used to adjust these results. There is one run per suite — no repeats, no
confidence intervals, no error bars. Timing is wall time for that one run.

## Common harness

- Model under test: **Qwen3.6-35B-A3B**, GGUF `qwen3.6-35b-a3b-ud-q3_k_m`.
  Served by the Unsloth Studio Desktop API in API-only mode, wrapping the
  existing daily-driver Qwen server. One model was in use; no second model was
  loaded or started for the closed/open suites.
- Requests: local OpenAI-compatible `POST /v1/chat/completions`, with the model
  name and an explicit provider id in every body (Studio will not route to the
  external Qwen without both). The provider-id value and the API key are not
  reproduced here; the key was read from a local file.
- Closed/open suites: `stream: false`, `temperature: 0`, `max_tokens` 2048
  (easy) or 4096 (hard and open-ended). No tools, no web access. Per-item
  timeout 120 s, pacing 0.2 s, results written incrementally after each item.
- Routing proof (all suites): every response echoed the model name and a
  `chatcmpl-…` id, carried the local engine's `timings` object
  (`prompt_n`, `predicted_n`, `draft_n`, `draft_n_accepted`), and returned the
  `server: unsloth-studio` header. The body is one JSON value followed by an
  SSE `data: [DONE]` sentinel even when streaming is off, so runners decoded
  only the leading JSON value. This confirms the external Qwen served the
  requests rather than an in-process Studio model.

### Suite naming caveat

The scorer sources are named `easy-mixed-12` and `hard-mixed-20` after their
original sizes. For this campaign the easy set was expanded to **20** items and
the hard set to **30** items; the directory names are stale. Totals from the
old 12-item and 20-item sets are therefore not comparable to these totals as
like-for-like counts.

## 1. Easy mixed QA — expanded, 20 items

*Measured:* **19 / 20 correct.** 20 API calls, 12.2 s wall time, 0 timeouts,
0 transport errors. Hand-written questions in the style of SWE-bench debugging,
GPQA, AIME and MMLU; question text was read as a literal from the source so it
is byte-identical to the source file.

Scoring was copied verbatim from the original `easy-mixed-12` scorer
(`qwen36_knowledge_eval.py`): parse the last `ANSWER:\s*([A-D]|\d+)` from
`content` + `reasoning_content`, with the original plain-token fallback from
`content` only.

| Category | Correct / Total |
|---|---:|
| swe | 4 / 5 |
| gpqa | 5 / 5 |
| aime | 5 / 5 |
| mmlu | 5 / 5 |
| **Total** | **19 / 20** |

| Metric | *Measured* value |
|---|---:|
| QA calls | 20 (plus 2 one-off diagnostic calls during harness validation) |
| Sum of per-call times | 8.36 s |
| Suite wall time | 12.2 s |
| Per-call min / max | 0.36 s / 0.49 s |
| Timeouts / transport errors | 0 / 0 |

**Failed item (measured):** `EASY-01`, category swe, expected B (6), parsed
C (10). Content was `ANSWER: C`; no transport or parse error. All 8 items added
on 2026-11-20 were correct; no item errored and none was scored `MANUAL`.

**Comparison (claimed baseline):** the older result was *claimed* 12 / 12 on
the original 12-item set, via a different transport. Not equivalent totals.
The first 12 expanded questions are byte-identical to the old 12; scored
per-item they are **11 / 12 (measured)**, with EASY-01 the single regression.
The 8 new items scored **8 / 8 (measured)**. The 12/12 figure is a summary
count from a different run; no per-item response data from it was used here.

## 2. Hard mixed QA — expanded, 30 items

*Measured:* **17 / 30 correct.** 30 API calls, 19.2 s wall time, 0 timeouts,
0 transport errors. Hand-written set with hand-verified answer keys.

Scoring was copied verbatim from the original `hard-mixed-20` scorer
(`qwen36_hard_eval.py`): parse the last `ANSWER:\s*([A-D]|\d+/\d+|\d+)` from
`content` + `reasoning_content`. **There is deliberately no fallback to a bare
token**, exactly as in the original scorer. This matters: 8 of the 13 misses
emitted a bare answer token with no `ANSWER:` prefix and are correctly scored
as misses under the existing logic.

| Category | Correct / Total |
|---|---:|
| code | 2 / 8 |
| science | 5 / 8 |
| math | 3 / 7 |
| knowledge | 7 / 7 |
| **Total** | **17 / 30** |

| Metric | *Measured* value |
|---|---:|
| QA calls | 30 (plus 2 one-off diagnostic calls during harness validation) |
| Sum of per-call times | 13.32 s |
| Suite wall time | 19.2 s |
| Per-call min / max | 0.38 s / 0.50 s |
| Timeouts / transport errors | 0 / 0 |

**Failed items (measured), expected → parsed:**

| ID | Category | Expected | Parsed | Raw content |
|---|---|---|---|---|
| HARD-02 | code | A | *(empty)* | `A` |
| HARD-03 | code | A | B | `ANSWER: B` |
| HARD-04 | code | B | *(empty)* | `C` |
| HARD-05 | code | D | *(empty)* | `D` |
| HARD-08 | science | A | *(empty)* | `A` |
| HARD-11 | math | 2333 | 2667 | `ANSWER: 2667` |
| HARD-12 | math | 4 | 2 | `ANSWER: 2` |
| HARD-21 | code | B | *(empty)* | `B` |
| HARD-23 | code | B | *(empty)* | `B` |
| HARD-25 | science | B | *(empty)* | `B` |
| HARD-26 | science | A | *(empty)* | `A) 2/7` |
| HARD-27 | math | 21 | 29 | `ANSWER: 29` |
| HARD-28 | math | 38 | 97 | `ANSWER: 97` |

**Format caveat — not a re-score.** Six of the 8 bare tokens are exactly the
answer key (`A`, `D`, `A`, `B`, `B`, `B` for HARD-02, 05, 08, 21, 23, 25): these
are format-compliance failures, not demonstrated knowledge failures. HARD-26
emitted `A) 2/7`, which contains the key letter but is not an exact token;
HARD-04 emitted a bare `C`, the wrong letter anyway. The easy run with a nearly
identical answer-format instruction produced `ANSWER: …` on all 20 items, so
this is intermittent formatting on the hard prompts, not transport truncation
(the response `predicted_n` counts match the short raw content, e.g. 2 tokens
for a single letter). **No alternative score is claimed.** The remaining 5
misses (HARD-03, 11, 12, 27, 28) did emit `ANSWER:` lines and are substantive
wrong answers.

**Comparison (claimed baseline):** the older result was *claimed* 20 / 20 on
the original 20-item hard set; totals are not equivalent. On the first 20
positions, **13 / 20 (measured)** kept the same outcome as the old run with 7
regressions — HARD-02, 03, 04, 05, 08, 11, 12. Four of those seven are
bare-token format failures; three are substantive. Across all 30 items there
are 8 bare-token failures, 4 of them (HARD-21, 23, 25, 26) in new positions
21–30. The 10 new items scored **4 / 10 (measured)**. Prompt text is not fully
like-for-like: of the first 20 items only 5 are byte-identical to the old JSON,
14 differ only in formatting (the old set displayed `Options:` labels and
extra blank lines), and 1 was substantively clarified by removing a named
distractor. Comparisons by index are indicative, not a controlled A/B test.
No per-item data from the old run was used to adjust these scores. A drop from
20/20 to 17/30 over a larger, partly reformatted set is not evidence of a
specified capability change; the measured facts are the per-item outcomes.

## 3. Open-ended suite — expanded, 30 items

*Measured:* **28 / 30 correct (93.3%).** 30 API calls, 411.5 s wall time,
0 timeouts, 0 transport errors, 0 manual items. Hand-written essay and proof
suite.

**Scorer reuse:** the original `run_suite.py` from `unified-suite-91` was
imported as a module (importing does not run its `main`), and its `SYSTEM_OPEN`,
`score_row`, `check_rubric`, `check_fixed`, `extract_answer` and `answer_text`
helpers were reused **unchanged**. No scorer file was edited. `score_row`
applies the rubric (≥ 0.8 of points required) and any `trap_patterns` override.
Prompt construction matches the original `ask()` for `open`/`proof` types.
All 30 rows of `questions/open_ended.jsonl` were read-only.

| Category | Total | Scored (auto) | Manual | Correct | Pct |
|---|---:|---:|---:|---:|---:|
| open_ended | 30 | 30 | 0 | 28 | 93.3% |
| **Total** | **30** | **30** | **0** | **28** | **93.3%** |

Rubric points passed on the 28 correct items ranged from 4/5 to 6/6. No item
errored and none needed a manual judgement.

| Metric | *Measured* value |
|---|---:|
| QA calls | 30 (plus 2 one-off diagnostic calls during harness validation) |
| Sum of per-call times | 405.64 s |
| Suite wall time | 411.5 s |
| Per-call min / max | 6.44 s / 39.59 s |
| Timeouts / transport errors | 0 / 0 |

Open-ended answers are long (up to 4096 tokens), which is why this suite is
much slower than the closed sets despite the same per-question timeout.

**Failed items (measured):** two misses, both preserved exactly as the
imported scorer produced them; no manual override was applied.

- `OPEN-MATH-01` — thermodynamics final-state item, rubric 4/4. Scored by
  `rubric+trap`: the rubric was fully satisfied (including recognition of an
  identical gas / no Gibbs mixing term), but the final answer gave the
  different-gases entropy (~18 J/K), matching a trap pattern. The trap
  override makes it incorrect by design. This was also the only miss in the
  older baseline.
- `OPEN-MATH-05` — irrationality proof, rubric 3/5. Scored by `rubric`: the
  response reached the right conclusion but did not match the rubric patterns
  for the squaring step or for deducing that the second variable is even, so
  it fell below the 0.8 threshold.

**Comparison (claimed baseline):** *claimed* 14 / 15 (93.3%) on the original
15-item `open_ended` set, scored with the same `run_suite.py` logic but served
directly. The expanded set has 30 items, so **14/15 and 28/30 are not
equivalent totals** — the identical 93.3% is a coincidence of counts, not a
claim of no change. Per-item where ids match, **all 15 shared ids (measured)
kept exactly the same correct flag** — 15 unchanged, 0 regressions, 0
improvements; rubric scores also matched on all 15. `OPEN-MATH-01` was the
baseline's only miss and remains a miss. The 15 new ids scored **14 / 15
(measured)**, the only new miss being `OPEN-MATH-05`. The baseline's other
categories (`swe`, `aime`, `mmlu`, `gpqa`, `traps`) were unrelated and not
re-run.

## 4. BrowseComp-HARD — 10 items (upper bound, not a clean measurement)

*Measured:* **9 / 10 correct.** 67 `web_search` tool calls, 340.5 s wall time,
0 stream errors, 0 timeouts. Hand-written 10-item research set; not official
BrowseComp items.

This suite used streaming with tools enabled (`enable_tools: true`,
`enabled_tools: ["web_search"]`, `permission_mode: "off"`). Non-streaming
requests had been observed to silently skip web search in an earlier smoke
test, so every request was streamed to completion. The system prompt plus each
item's question text only were sent; the answer key and metadata fields were
not shown to the model. One request per item, hard cap 600 s. Tool activity
was counted from `tool_start`/`tool_end` events. Scoring was manual: all parts
of the key had to be present, partial = incorrect. Ground truth came from the
hand-written key field, re-verified earlier on 2026-11-20; the questions were
never shown to the model.

| ID | Topic (shortened, no question text) | Tool calls | Elapsed | Correct? | Flag |
|---|---|---:|---:|---|---|
| H01 | 2025 sports final: club, early scorer, departed manager | 11 | 54.1 s | yes | — |
| H02 | 2025 physics laureates and their employers | 6 | 30.1 s | yes | — |
| H03 | 2025 physics circuit element and pioneer | 3 | 19.6 s | yes | possibly guessed / leaked intermediate (< 4) |
| H04 | ski-mountaineering debut Games: cauldron lighters, top nation, golds | 7 | 35.8 s | yes | — |
| H05 | 2026 Games: closing venue, cauldron lighters, exact dates | 0 | 5.7 s | **no** | possibly guessed / leaked intermediate (< 5) |
| H06 | 2025 Amazon summit: mission, president, referenced COP decision year | 24 | 101.1 s | yes | — |
| H07 | adaptation-finance pledge → next Winter Games: nation and medal total | 4 | 25.5 s | yes | possibly guessed / leaked intermediate (< 5) |
| H08 | 2025 club final: runner-up and both scorers | 5 | 25.2 s | yes | — |
| H09 | laureate's startup and departed club manager's surname | 4 | 22.6 s | yes | possibly guessed / leaked intermediate (< 6) |
| H10 | 2026 opening stadium and physicist behind the named junction | 3 | 20.9 s | yes | possibly guessed / leaked intermediate (< 6) |

**Total: 9 / 10 (measured).** Tool calls by item: 11, 6, 3, 7, 0, 24, 4, 5,
4, 3 (67 total). Question text and answer keys are withheld from this draft.

### Why this is an upper bound, not a clean measurement

- **H05 is the only wrong answer.** It returned in 5.7 s with **zero** tool
  calls despite tools being enabled, and the stream had no error. The model
  answered from memory: wrong closing venue, wrong cauldron lighters, only the
  dates correct. Tool use was never triggered on this request.
- **Five items carry the `min_turns` flag** (H03, H05, H07, H09, H10). For the
  four correct flagged items the traces show genuine searches with round ids,
  so the flags are a mechanical "calls below threshold" convention, not proof
  of leaked ground truth. H03 also contained an early wrong speculation before
  settling on the correct final answer. Still, five flagged items out of ten
  means the 9/10 figure should be read as an upper bound on demonstrated
  tool-grounded performance, not a clean measurement.
- **H06 log discrepancy (measured):** 24 SSE `tool_start` events but 22
  `execute_tool` log lines in the server log for that request window; the two
  extra calls are visible in the SSE stream only. The other nine items matched
  per-item log counts exactly (65 log lines in total).
- The legacy desktop-app log had no new tool entries for this campaign; the
  API-only server's own log for the window was used for the cross-check.
- Output text included the model's visible "Searching: …" progress lines mixed
  with the answer; scoring used the `FINAL:` line and its surrounding
  conclusions.
- Multi-hop traces were observed on several items (e.g. a wrong lead
  self-corrected over 7 rounds on H01; 24 calls / 10 rounds on H06 resolving a
  referenced decision; page reads issued through the same tool with a `url`
  argument on H08). These are qualitative observations from the single run,
  not scored results.

## Machine state and side effects (measured)

| Check | Before | After |
|---|---|---|
| Free RAM, closed/open suites | 14442.8 MB free / 31860.6 MB total | 15204.1 MB free / 31860.6 MB total (+761.3 MB) |
| Free RAM, BrowseComp suite | 14.16 GB / 31.11 GB total | 13.77 GB / 31.11 GB total (−0.39 GB) |
| Repository commit | unchanged | unchanged (same hash) |
| Tracked-file modifications | none | none |

No process was killed. The existing direct-serve Qwen process and the Studio
API server were left running; no model, config, question or scorer file was
modified. The Studio API server was started for the BrowseComp campaign and
left running for the next one.

## Limits

- One run per suite: no repeats, so no variance estimate and no claim about
  stability. Small sets (20, 30, 30, 10 items) give coarse percentages; one
  item moves the easy result by 5 points and the BrowseComp result by 10.
- All question sets are hand-written locally and are not official benchmarks.
  The "BrowseComp-HARD" name does not mean official BrowseComp items.
- Baseline comparisons are *claimed* numbers from earlier runs on different
  transports and, in the hard case, partly reformatted prompts. They are
  indicative only, not controlled A/B tests.
- Scorer behaviour is preserved, not corrected: the hard scorer's lack of a
  bare-token fallback and the open-ended trap override both count items as
  wrong by design. No re-score or manual override is claimed.
- The BrowseComp result is an upper bound for the reasons above.

## Artifacts (generic names)

- Raw per-item results: `easy-qwen36-unsloth.json`, `hard-qwen36-unsloth.json`,
  `open_ended-qwen36-unsloth.json`, `qwen36-unsloth-results.json`.
- Runners: `easy_run.py`, `hard_run.py`, `open_run.py`,
  `run_qwen36_unsloth.py`, with shared client `common.py`.
- Scorers reused unchanged: `qwen36_knowledge_eval.py`, `qwen36_hard_eval.py`,
  `run_suite.py`; BrowseComp scoring script `score_qwen36_unsloth.py`.
- Questions read-only: `questions/open_ended.jsonl`; baseline file
  `qwen36-baseline-corrected-20261119-174109.json` (open-ended category only).
