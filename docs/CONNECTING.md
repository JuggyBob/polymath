# Connecting to a model

The direct-HTTP QA runners talk to an **OpenAI-compatible** chat-completions
endpoint:

```
POST http://<host>:<port>/v1/chat/completions
```

The agent-harness suites (repair fixtures, Craft, LFM and the BrowseComp web
set) do not call HTTP themselves; see their sections below.

You choose the port. The direct-HTTP runners prompt for it if you do not pass
`--port`; pressing Enter selects 8080. Harness-driven and cloud-API suites use
their own configuration instead.

## Local server example

```powershell
llama-server -m model.gguf -c 32768 --port 8080
# or: strata launch ... --port 8080
# or: vllm serve <model> --port 8080
```

Then:

```powershell
python run_suite.py --port 8080
```

The direct-HTTP runners send no API key. If your server requires one, put a
local proxy in front of it that adds the header, or use `--base-url` to point at
an endpoint that handles authentication itself. Never edit a key into a runner.
The optional BrowseComp cloud-API runner is the exception: it reads a key from a
local file and sends it as a Bearer token (see `qa/browsecomp/README.md`).

## Flags common to the QA runners

| Flag | Meaning |
|---|---|
| `--port` | server port; prompts interactively if omitted |
| `--host` | server host, default `127.0.0.1` |
| `--base-url` | full chat-completions URL; overrides host/port |
| `--model` | model id as the server knows it; prompts if omitted |
| `--label` | tag used in output filenames |
| `--limit N` | run only the first N questions (smoke test) |
| `--dry-run` | validate question files without calling the model |
| `--timeout` | per-request timeout in seconds |
| `--max-tokens` | generation budget |
| `--temperature` | sampling temperature; 0.0 by default |

## Repair fixtures

Repair fixtures do **not** call the model. They launch a coding-agent harness
in a copied `task/` directory. Configure that harness to use your endpoint:

- Hermes: set the provider/base URL in its profile to your local server.
- Claude Code / Codex / other agents: use their equivalent base-URL setting.

Then run the agent in `run-<label>/` and grade the directory with the scorer.
See `repair/README.md` for the full sequence.

## BrowseComp-style research

These need a harness with working `web_search` and `web_fetch` tools. A plain
chat endpoint without tools cannot run them. See `qa/browsecomp/README.md`.

## Troubleshooting

- **Connection refused** — check the server is listening on the port you gave.
- **404 on `/v1/chat/completions`** — your server may expose a different path;
  pass the full path with `--base-url`.
- **Empty answers** — increase `--max-tokens`; reasoning models can spend the
  whole budget before producing the final `ANSWER:` line.
- **Every answer is `MANUAL`** — you selected a category with rubric scoring and
  no machine-checkable key; that is expected.
