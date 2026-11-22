# BrowseComp-style multi-hop set (10 questions, 2026-11-20)

A harder successor to `browsecomp-web-10`. The original set had 5 easy + 5
"hard" items, but a strong model with live web tools solved all 10 (Qwen3.6:
10/10; the hardest items took up to 13–14 tool calls, hard-item range 5–14:
H1 13, H2 14, H3 6, H4 12, H5 5). These 10 questions are built to require
several dependent research steps instead.

Current status: a tool-capable run scored **9/10** with **67 tool calls** over
**340.5 s** on 2026-11-20. The results are in `qwen36-unsloth-results.json`.

Five of the ten items are flagged `possibly guessed / leaked intermediate`
and H05 used zero tool calls; treat 9/10 as an upper bound, not a clean
measurement (see `results/README.md`).
The original `browsecomp-web-10` files are preserved alongside this set.

Chronology: this README was first written at 17:05:58, the run script was
created at 17:21:47 and the results at 17:28:33 on 2026-11-20. The "no model
has been run" statement was accurate when written and is no longer current.

These are hand-written questions in the style of BrowseComp. They are **not**
official benchmark items and must never be reported as such.

## What makes them multi-hop

Every question **hides the intermediate entity**. The agent has to discover
fact A before it can even formulate the search for fact B, and most items add
a third fact from a different domain. Concretely:

- H01 never says "Chelsea" — you must identify the New Jersey 3-0 final first,
  then look up its scorers, then find the departing manager.
- H04 never says which Olympics — the debut sport is the only handle, and the
  answer then needs the cauldron lighters and the medal table.
- H07 and H09 and H10 cross two unrelated domains (climate/sport, science/sport),
  so one source page cannot contain the answer.

Each item records `hops` (the required intermediate findings) and `min_turns`
(an estimated floor on tool calls). Record the actual tool-call count from the
runner: if a model answers one of these in 1–2 calls, either it guessed or the
question leaked its intermediate entity.

## Files

- `browsecomp_hard_questions.json` — questions, keys, hops and source notes.
  **Ground truth; do not show it to the model under test.**
- `browsecomp_hard_run.py` — **OBSOLETE as written**: it still assumes Goose and
  the old Goose web MCP extension. Goose was deleted from this machine. Do not
  run it until it is rewritten for Hermes (which has `mcp_web.py` with
  `web_search`/`web_fetch`) or for Unsloth's API with `enable_tools: true`.
- Ground truth was inherited from the set verified on 2026-11-17, then
  independently re-verified by live web search on **2026-11-20** against
  primary sources: NobelPrize.org (press release and scientific background),
  Google and Qolab announcements, the PNAS laureate profile; Olympics.com's
  Games page, medal table and ceremony reports; the UNFCCC COP30 executive
  report, COP30's official site and UN News; and FIFA.com's match report,
  records and "Chelsea confirm Maresca exit" article. One caution from that
  check: a BBC article said Norway collected "18 medals", but the official
  Olympics.com table gives 18 gold and 41 total — the table is authoritative
  and our key uses it.

## Running

The original Goose runner is deprecated (Goose is no longer installed). Two
working paths exist:

1. A tool-capable cloud API - see `run_qwen36_unsloth.py` and the
   [browsecomp README](../README.md). This is how the recorded 9/10 result was
   produced.
2. A local agent harness with `web_search`/`web_fetch` tools pointed at your
   own OpenAI-compatible server. Give the harness only the `q` field from
   `browsecomp_hard_questions.json`, never `answer` or `hops`.

These questions need more steps than the original 12-turn limit allowed.
Record actual tool-call counts; a correct answer in 1-2 calls is not
trustworthy.

## Scoring

Manual, same as before: every part of the answer must be present. LFM's
half-right H2 in the original set was counted wrong, and that convention is
kept. Count a missing part as a miss; count a wrong part as a miss even if the
other parts are right. Report per-item tool calls and elapsed time alongside
the score, since a low tool count makes the result untrustworthy.
