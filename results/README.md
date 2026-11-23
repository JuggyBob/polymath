# Historical results

The JSON files kept alongside the suites are **observations from one machine on
specific dates**, not a leaderboard. They are preserved for traceability, not
as a ranking of models.

## What is here

- Closed-book results for the easy and hard sets.
- Open-ended baselines in `qa/open-ended/baselines/`.
- Repair-fixture scores in each `repair/<language>/v*/` folder.
- The v7 campaign, design, audit record and attempted Inkling comparison in
  [`docs/V7-RESULTS.md`](../docs/V7-RESULTS.md),
  [`docs/V7-REPORT.md`](../docs/V7-REPORT.md),
  [`docs/V7-AUDIT.md`](../docs/V7-AUDIT.md) and
  [`docs/V6-INKLING-COMPARISON.md`](../docs/V6-INKLING-COMPARISON.md). Run
  artifacts and per-run score JSONs are deliberately ignored; scores are
  reported in the path-free documents under `docs/`.
- BrowseComp results in `qa/browsecomp/*/`.
- Older LFM runs under `qa/closed-book/lfm25-baseline/`, and Goose-era repair
  runs under `repair/python/goose_qwen/` and `repair/python/goose_lfm/`.

## Caveats that matter

1. **Question-set versions changed.** The folder names are historical:
   `easy-mixed-12` now holds 20 questions and `hard-mixed-20` holds 30.
   Older results cover the original 12 and 20 question sets and are not
   directly comparable with newer ones.
2. **Some headline numbers have known issues.**
   - The original hard-set evaluator concatenated response and reasoning and
     took the last `ANSWER:` match; replaying one saved response changes
     20/20 to 19/20. The shipped runner in this repository scores content only,
     which fixes the bug.
   - The original Craft scorer subtracted `w:bCs`/`w:iCs` counts its regex never
     counted, reporting 8/14 where the document deserved 10/14. The scorer here
     is fixed. Its font threshold is also corrected to the required 16 pt.
   - A v5 Rust re-run scored 67/69; this is preserved rather than hidden behind
     the earlier 69/69 result.
3. **BrowseComp hard set: 9/10 with caveats.** The run used a tool-capable cloud
   API with `web_search` only, took 67 tool calls and 340.5 s. Five of the ten
   items carry a `possibly guessed / leaked intermediate` flag, and one had
   zero tool calls. Treat 9/10 as an upper bound, not a clean measurement.
4. **Metadata is incomplete in old files.** Most results do not record model
   quant, context length, engine version or question-set hash. Do not compare
   across engine changes without checking the reports.
5. **NOT RUN items are intentional.** Missing rows in older campaigns mean the
   test was not run, not that it scored zero.

## If you publish new results

Every runner records the endpoint, model and temperature. The direct-HTTP
runners also record `max_tokens` and total wall-clock time; the BrowseComp
cloud-API runner records per-item elapsed time only, with no `max_tokens` field
and no total wall-clock field. Keep those fields. Add the
quant, context length and engine version in your report so future readers can
tell what changed.
