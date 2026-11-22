# BrowseComp-style research sets

Two hand-written, multi-hop research sets. They are written *in the style of*
BrowseComp and are **not** official BrowseComp items. Do not report scores as
official benchmark results.

| Set | Folder | Questions | Status of runners |
|---|---|---:|---|
| Web set (v1) | `web-10/` | 10 | Original Goose runner preserved but **deprecated** |
| Hard set | `hard-10/` | 10 | Cloud-API runner works; local Goose runner deprecated |

All 20 ground-truth answers were independently verified against primary sources
(NobelPrize.org, FIFA / Chelsea FC, Olympics.com / IOC / CONI / Reuters,
UNFCCC / UN News and medal tables). The keys are correct as of 2026.

## What makes the hard set hard

Every question hides the intermediate entity. You must discover fact A before
you can even formulate the search for fact B, and most items add a third fact
from a different domain. A model that answers one of these in 1–2 calls either
guessed or the question leaked its intermediate entity.

## What you need

1. **A model with working web tools.** Either:
   - a harness with `web_search` and `web_fetch` (e.g. Hermes with its web MCP
     tools), pointed at your local OpenAI-compatible server, or
   - a cloud API that supports tool use (the recorded 9/10 run used Unsloth
     with `enable_tools: true`).
2. **No API key for the local path.** The included MCP server searches
   DuckDuckGo's HTML endpoint and fetches pages directly. If your harness or
   provider requires a key, configure it there — nothing in this repo stores
   credentials.
3. **Python 3.10+** with `requests` and `mcp` if you use the bundled
   `web_mcp_server.py`:

   ```powershell
   python -m pip install requests mcp ddgs
   ```

4. **Ground truth is private to the grader.** Never put
   `browsecomp_hard_questions.json` or `browsecomp_questions.json` in the
   model's prompt or workspace. They contain the answers and the `hops`.

## Running the web set with a local harness

The legacy `browsecomp_run.py` targeted Goose, which is no longer installed.
It is kept for reference. To run the set today:

1. Start your local OpenAI-compatible server on a port you choose.
2. Configure your agent harness with `web_search` / `web_fetch` tools pointing
   at that server.
3. Give the harness the questions from `web-10/browsecomp_questions.json` —
   **only the `q` field**, never `answer` or `hops`.
4. Ask for a final line `FINAL: <answer>` and record the tool-call count for
   each question.
5. Verify answers against the key with a human or the included scoring helper.

## Running the hard set through a tool-capable API

`hard-10/run_qwen36_unsloth.py` shows a working example using an API with
`enable_tools: true`. Its endpoint, provider id, key-file path and
question/result paths are fixed constants near the top of the file; edit those
for your provider. Its only flags are `--start`, `--end`, `--timeout` and
`--force`:

```powershell
cd hard-10
python run_qwen36_unsloth.py --start 1 --end 10 --timeout 600
python score_qwen36_unsloth.py
```

`score_qwen36_unsloth.py` also has no flags and reads
`qwen36-unsloth-results.json` from its own fixed path. No key is stored in the
repository; the runner reads one from the local file named by `KEYFILE`.

The recorded run produced **9/10** with **67 tool calls** over **340.5 s**.
Those numbers are from one observation on one machine, not a robust estimate.

## The bundled MCP web server

`web-10/web_mcp_server.py` exposes two tools, `web_search` (DuckDuckGo HTML)
and `web_fetch` (HTTP plus HTML-to-text). It needs no API key. Notes:

- It scrapes DuckDuckGo's HTML endpoint with a browser user-agent. That is
  brittle and may break or violate terms of service. Use an official search
  API in production if you need reliability.
- It fetches arbitrary URLs. Only run it in a trusted local environment; it
  has no SSRF protection, content-type checks or size limits.
- Search results can be `None`; treat the tool as best-effort.

## Historical note on the hard-set README

The original README said no model had been run on the hard set. That was true
when the README was written (17:05:58 on 2026-11-20); the run script was
created at 17:21:47 and the results at 17:28:33 the same day. The 9/10 result
is the current state. The staged README reflects this chronology.
