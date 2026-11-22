> These are hand-written BrowseComp-style items, not official benchmark items.
> Scores below must never be reported as official benchmark results.
# BrowseComp-style test — Qwen3.6 vs LFM2.5 through Goose (2026-11-17)

10 current-events research questions (5 easy, 5 hard). Ground truth verified by
web search on 2026-11-17 from primary sources (NobelPrize.org, FIFA.com, COP30
official, Olympics.com, Wikipedia medal table).

**Real browsing:** Goose was given two live MCP tools — `web_search` (DuckDuckGo,
via `ddgs`) and `web_fetch` (HTTP + HTML-to-text). The system prompt required
searching and fetching sources before answering. Answers were captured from
Goose's JSON output. Every question records its tool-call count so we can
confirm it browsed rather than guessed. Both models: 64K context, thinking off,
`--no-profile` + web MCP extension.

## Scores

| Model | Easy (5) | Hard (5) | Total |
|---|---:|---:|---:|
| **Qwen3.6-35B-A3B** | 5/5 | 5/5 | **10/10** |
| **LFM2.5-24B-A2B** | 4/5 | 1/5 | **5/10** |

LFM totals count a wrong or missing answer as incorrect. Two answers (H2, H4)
were half-right; see notes.

## Per-question results

### E1 (easy) — Who won the 2025 FIFA Club World Cup final, score, runner-up?
**Key:** Chelsea beat Paris Saint-Germain 3–0.

- **Qwen (9.5 s, 1 tool): CORRECT.** "Chelsea won the 2025 FIFA Club World Cup,
  defeating Paris Saint-Germain 3–0 in the final."
- **LFM (9.7 s, 5 tools): CORRECT.** "Chelsea won the 2025 FIFA Club World Cup
  final 3–0 over Paris Saint-Germain, with PSG as the runner-up."

### E2 (easy) — Which Brazilian city hosted COP30 (Nov 2025)?
**Key:** Belém.

- **Qwen (8.7 s, 2 tools): CORRECT.** "Belém"
- **LFM (6.5 s, 4 tools): CORRECT.** "Belém, Pará, Brazil"

### E3 (easy) — Which two cities co-hosted the 2026 Winter Olympics, and when?
**Key:** Milan and Cortina d'Ampezzo; February 2026.

- **Qwen (6.5 s, 1 tool): CORRECT.** "Milan and Cortina d'Ampezzo, Italy ...
  February 2026 (Feb 6–22)."
- **LFM (19.1 s, 11 tools): CORRECT.** Same answer with exact dates.

### E4 (easy) — Name the three 2025 Nobel Physics laureates.
**Key:** John Clarke, Michel H. Devoret, John M. Martinis.

- **Qwen (8.4 s, 2 tools): CORRECT.** All three named, cited nobelprize.org.
- **LFM: FAILED (no answer).** With 12-turn limit and again with 35-turn limit
  it burned all turns searching and returned "I've reached the maximum number
  of actions I can do without user input" instead of an answer.

### E5 (easy) — Who topped the 2026 Winter Olympics medal table?
**Key:** Norway (18 gold, 41 total).

- **Qwen (16.4 s, 4 tools): CORRECT.** "Norway" (also noted USA second).
- **LFM (9.4 s, 5 tools): CORRECT.** "Norway ... 18 gold, 41 total."

### H1 (hard) — Nobel laureate at Google Quantum AI + laureate's quantum startup?
**Key:** Google (Google Quantum AI) and Qolab.

- **Qwen (41.2 s, 13 tools): CORRECT.** "The tech company is Google (Google
  Quantum AI), and the quantum startup is Qolab."
- **LFM: FAILED (no answer).** Hit the 35-turn cap (35 tool calls) and returned
  the max-actions message.

### H2 (hard) — Who scored the opening two goals in the Club World Cup final, and which manager left?
**Key:** Cole Palmer; Enzo Maresca.

- **Qwen (49.5 s, 14 tools): CORRECT.** "Cole Palmer scored the opening two
  goals; the manager was Enzo Maresca."
- **LFM (17.8 s, 10 tools): HALF-RIGHT → counted wrong.** Got Cole Palmer right,
  but said the departing manager was "Gareth Southgate" (wrong — he manages
  England). On the earlier 12-turn run it instead guessed "Thomas Tuchel"
  (also wrong). It never found the correct name, Enzo Maresca.

### H3 (hard) — Who lit the Milan cauldron at the 2026 Winter Olympics, and which sport debuted?
**Key:** Deborah Compagnoni and Alberto Tomba; ski mountaineering.

- **Qwen (79.6 s, 6 tools): CORRECT.** "Alberto Tomba and Deborah Compagnoni;
  ski mountaineering made its Winter Olympic debut."
- **LFM: FAILED.** Hit the 12-turn cap on the first run, then **timed out at
  600 s** with 0 completed tool results on the 35-turn run — it looped on the
  web tools and never answered.

### H4 (hard) — COP30 summit president + which earlier COP decision's "fossil fuels" language was referenced?
**Key:** André Corrêa do Lago; the COP28 "UAE Consensus".

- **Qwen (46.8 s, 12 tools): CORRECT.** "André Corrêa do Lago, and the final
  text referenced the UAE Consensus from COP28 (Dubai 2023)."
- **LFM (65.2 s, 30 tools): HALF-RIGHT → counted wrong.** Correctly identified
  the COP28/UAE Consensus reference, but named **Lula da Silva** as summit
  president. Lula is Brazil's president who opened the summit; the COP30
  president was André Corrêa do Lago.

### H5 (hard) — Name the Josephson junction and the detector Clarke pioneered.
**Key:** Josephson junction; SQUID.

- **Qwen (20.3 s, 5 tools): CORRECT.** "Josephson junction ... SQUID
  (Superconducting Quantum Interference Device)."
- **LFM (25.0 s, 11 tools): CORRECT.** "Josephson junction ... SQUID ... based
  on the same Josephson tunnelling physics." (Added a wrong aside that Clarke
  did this "at MIT in the 1970s" — core answer correct.)

## Speeds (PolyStrata server logs)

| | Qwen | LFM |
|---|---:|---:|
| Decode during browsing | ~83–114 tok/s | ~83–148 tok/s |
| Prefill (cached) | ~230–980 tok/s | ~280–1430 tok/s |

LFM is still the faster decoder per token. But its wall-clock times were often
worse because it made many more tool calls (up to 35) and looped — Qwen reached
answers with 1–14 calls and gave clean FINAL lines.

## RAM / commit

| | Qwen | LFM (12-turn run) | LFM (35-turn run) |
|---|---:|---:|---:|
| Peak commit | 29.1 GiB | 25.7 GiB | 29.8 GiB |
| Min free | 16.9 GiB | 13.9 GiB | 17.3 GiB |

No paging. Final state: all servers off, 15.6/57.1 GiB commit, 19.9 GiB free.

## Key finding

Qwen reliably **used the web tools and stopped when it had an answer** —
10/10, with source citations. LFM's problem was not knowledge; it was
**agent self-termination**. On 3 of 10 questions it never produced an answer
(tool loop → turn cap or 600 s timeout), and on 2 more it retrieved search
results but still guessed a wrong fact. This is the same Goose tool-loop issue
seen earlier, now on live web tools: LFM keeps searching instead of concluding.
When it did conclude, its facts were mostly right.

Files: `browsecomp_questions.json` (questions + verified keys + sources),
`browsecomp-qwen.json`, `browsecomp-lfm.json` (full answers, tool calls, token
usage, speeds), `web_mcp_server.py` (the MCP web tools), `browsecomp_run.py`.
