# QA suites

This folder contains **every question-answering suite** in the repository. All
of them are hand-written. They are written *in the style of* SWE-bench, AIME,
MMLU, GPQA and BrowseComp — they are **not** official benchmark items and must
never be reported as such.

The direct-HTTP QA runners speak plain HTTP to an **OpenAI-compatible**
chat-completions endpoint. You supply the port. Agent-harness and cloud-API
suites use their own configuration instead (see the table below).

## Quick start

Start any OpenAI-compatible server first. For example:

```powershell
llama-server -m model.gguf -c 32768 --port 8080
```

Then run a suite from this `qa/` folder. The direct-HTTP runners ask for the port
if you do not pass `--port`:

```powershell
cd open-ended
python run_suite.py --port 8080                 # interactive port prompt if omitted
python run_suite.py --port 8080 --dry-run       # validate question files only

cd ../closed-book/easy-mixed-12
python run_closed_book.py --port 8080
```

## Suites

| Suite | Folder | Questions | Connection | Scoring |
|---|---|---:|---|---|
| Unified open suite | `open-ended/` | 96 default / 106 with BrowseComp | Direct HTTP | Exact / numeric / rubric / traps |
| Easy mixed set | `closed-book/easy-mixed-12/` | 20 | Direct HTTP | Exact letter/number |
| Hard mixed set | `closed-book/hard-mixed-20/` | 30 | Direct HTTP | Exact letter/number |
| LFM2.5 baseline | `closed-book/lfm25-baseline/` | 12 + 20 | Agent harness | Exact letter/number |
| Office document task | `closed-book/craft-office-hard/` | 1 | Agent harness | Scripted `.docx` checks |
| BrowseComp-style web set | `browsecomp/web-10/` | 10 | Agent + web tools | Operator-verified keys |
| BrowseComp-style hard set | `browsecomp/hard-10/` | 10 | Cloud API + tools | Operator-verified keys |

> **Folder names are historical.** `easy-mixed-12` now contains 20 questions,
> `hard-mixed-20` contains 30, and `open-ended/` contains 96 in its default
> categories. The content was expanded over time; the names were not changed so
> old baselines remain traceable.

## What every runner produces

1. **Live progress** — a bar, current question id/category, verdict
   (`OK` / `MISS` / `MANUAL` / `ERROR`) and a running score as the run proceeds.
2. **A final score** — per-category breakdown plus total, with the endpoint,
   model, temperature, `max_tokens` and wall-clock time printed above it.
3. **A result JSON** — all answers, parsed answers, correctness, timings and
   any `reasoning_content` the server returned.
4. **Reasoning files** — one Markdown file per question in
   `reasoning/<label>-<timestamp>/`, containing the question, expected answer,
   the model's full response, its reasoning, how it was scored and server
   timings. These are written at the end of the run, never during it.

## Connecting to the model

- Direct HTTP suites use `http://<host>:<port>/v1/chat/completions` with a
  standard OpenAI body. No API key is sent, so a keyless local server works.
- If your server requires a key, use `--base-url` with a proxy that adds it, or
  set the server's own key handling. The runners deliberately do not embed
  credentials.
- The agent-harness suites do not call HTTP themselves. They launch your agent
  in a workspace; configure that agent to point at your server. See each
  subfolder README.

## Reproducibility caveats

- Scores are comparable only when **model, quant, context length, temperature
  and `max_tokens` match**. All of those are recorded in each result JSON.
- Most runs were single observations on one machine, not repeated campaigns.
  Treat differences of a few percent as noise.
- `MANUAL` items are not included in the automatic score. `NOT RUN` items are
  explicitly preserved in the historical reports under `results/`.
- Open-ended rubric scoring uses keyword patterns and a threshold of 0.8. It is
  a heuristic, not a semantic judge.
