# Methodology and reproducibility

## What these tests are

Hand-written questions and repair tasks used to choose and check a local model.
They are written in the style of well-known benchmarks but are **not** official
benchmark items. The questions, answer keys and hidden tests are public in this
repository, so scores produced after publication are not blind.

## Fair comparison checklist

To compare two models, keep these constant:

- question-set version (record the file hash);
- model, quant and engine version;
- context length;
- temperature and `max_tokens`;
- the agent harness and its version (for repair fixtures);
- the prompt given to the agent (for repair fixtures).

The direct-HTTP runners record endpoint, model, temperature, `max_tokens` and
wall-clock time in every result JSON. The BrowseComp cloud-API runner records
endpoint, model, temperature and per-item elapsed time but not `max_tokens` or
a total wall-clock field. Add quant, context and engine version in your own
report.

## Scoring

- **Fixed answers** - exact normalised match against `accept`. All runners
  apply a 0.1% relative tolerance only to non-integer numeric keys; integer keys
  must match exactly.
- **Rubric items** — keyword patterns; at least 80% of points must match. This
  is a heuristic, not a semantic judge.
- **Traps** — a value mentioned and explicitly rejected in the final answer is
  not counted as a wrong answer. A value adopted in the final answer is.
- **Repair fixtures** — hidden tests are injected only at grading time; a
  solution that breaks a baseline-passing visible test is zeroed. See
  `repair/SECURITY.md` for known gaps.

## Statistical limits

Most historical results are single observations. Differences of a few percent
are noise. Repeat a run at least three times if a decision depends on the gap.
`NOT RUN` means exactly that — the test was not attempted, not that it scored
zero.

## Known historical issues

These were found by independent audit and fixed in this staging:

- the original hard-QA evaluator read `ANSWER:` from response+reasoning and
  changed one saved 20/20 to 19/20;
- the Craft scorer understated a formatted document as 8/14 instead of 10/14;
- `OPEN-EE-03` had a rubric pattern that matched every model;
- `TRAP-02` depended on a previous question that is not sent in an independent
  API call;
- a 1% tolerance accepted neighbouring integers on AIME answers.

Historical results in `results/` retain their original caveats rather than
being silently re-scored.
