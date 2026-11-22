> This is a hand-written local agent task, not an official benchmark item.
> Scores below must never be reported as official benchmark results.
# CraftSuite hard document test — Qwen vs LFM (2026-11-17)

A genuinely hard agentic task: build a richly formatted .docx through the
WordCraft MCP — headings, bold, italic, custom color, font size, highlight,
center alignment, a table, and an **embedded image** — then save it.

Both models ran the SAME task through Goose CLI v1.59.2 at 64K context, with
the WordCraft MCP registered. Scoring is **independent**: `craft_score.py`
unzips the saved docx and checks the XML directly (text runs, pStyle headings,
`w:b`/`w:i`, `w:color`, `w:sz`, `w:highlight`, `w:jc`, `w:tbl`, `word/media/`).
It does not trust anything the agent says.

## Results
Note: these 8/14 figures are the original recorded scores from the buggy
scorer, which subtracted `w:bCs`/`w:iCs` counts its regex never matched. Under
the fixed scorer the same document scores 10/14 (see `docs/METHODOLOGY.md` and
`results/README.md`). 8/14 is retained only as the historical value.

| Run | Score | Tool calls | Time | Outcome |
|---|---:|---:|---:|---|
| **Qwen (full profile, 80 turns)** | **8/14** | 80 | 161 s | Saved docx; hit turn cap but produced real work |
| **Qwen (50 turns, batch task)** | **8/14** | 10 | 86 s | Saved docx cleanly — best run |
| LFM (full profile, 50 turns) | 0/12 | 50 | 46 s | Never used WordCraft; looped on `ls -la /workspace` ~49× |
| LFM (--no-profile, 50 turns) | 0/12 | 50 | 34 s | Never used WordCraft; looped on `web-search`/`load_skill` ~48× |

## Qwen detail (best run, 8/14)

Qwen used the batch approach in 10 tool calls (list_commands ×7, batch, shell,
get_text) and saved a real docx.

| Check | Result |
|---|---|
| text "Project Aurora" | PASS |
| text "Quarterly Report" | PASS |
| text "Executive Summary" | FAIL |
| text "Q3 2026" | FAIL |
| Heading1 style | FAIL (0) |
| Heading2 style | PASS (2) |
| Bold run | FAIL (0) |
| Italic run | FAIL (0) |
| Non-black color | PASS (FF0000) |
| Enlarged font | PASS (36 half-pt = 18pt) |
| Highlight | PASS (yellow) |
| Embedded image | PASS (image1.png, 1572 bytes) |
| Table | PASS (1) |
| Alignment | FAIL (only left) |

**Why the failures:** Qwen's batch interleaved `select.text "X"` → `format.bold`,
then `text.insert "Y"`. In WordCraft, `text.insert` **replaces the current
selection** — so each new insert overwrote the previously formatted text. That's
why "Executive Summary"/"Q3 2026" and their bold/italic vanished, while the
last unselected insert and the standalone format commands (color, size,
highlight, image, table) survived. This is a real reasoning error about tool
state, not a harness or scorer issue.

## LFM detail

Both LFM runs never reached the document task at all:

- **Full profile:** `shell` ×49, mostly `ls -la /workspace` / `dir /workspace`
  (a non-existent Linux path) in a loop.
- **--no-profile:** `web-search` ×48 + `load_skill` ×2, looping instead of
  building the document.

This is the same tool-seeking/self-termination failure seen in the web research
test: LFM keeps searching for the "right" tool instead of committing to the
task and concluding. On a stateful, multi-step tool task it never even started.

## RAM

- Qwen: peak commit 32.8 GiB, min free 12.7 GiB.
- LFM: peak commit 30.1 GiB, min free 9.1 GiB.
- No paging. Final state: all servers off, 18.9/57.1 GiB commit, 17.6 GiB free.

## Bottom line

For agentic tool work — formatting a document, embedding an image, driving an
app through MCP — **Qwen is clearly the capable one**: it actually used the
tools, saved a real file, and got 8 of 14 checks right on its first clean run.
Its mistakes are fixable reasoning errors (tool state), not an inability to act.

LFM failed both times by looping on irrelevant tools and never touching
WordCraft. For anything agentic, it is not usable on this harness right now.

Files: `craft_doc_task.md` (task), `craft_score.py` (verifier),
`craft_hard_run.py` (runner), `craft-hard-qwen-result.docx` + `-score.txt`,
`craft-hard-lfm-fullprof-*` and `craft-hard-lfm-noprof-*` (attempts), and the
`-goose.txt` transcripts.
