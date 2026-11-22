# Local Model Harness

A set of hand-written, repeatable tests for choosing and checking a local AI
model. It covers question answering, multi-hop web research and agentic code
repair in four languages.

**These are not official benchmark items.** The questions are written *in the
style of* SWE-bench, AIME, MMLU, GPQA and BrowseComp. Scores are useful for
comparing models on your own machine under conditions you control. They must
never be reported as official benchmark results.

## What is inside

| Area | Folder | What it tests |
|---|---|---|
| QA suites | [`qa/`](qa/README.md) | 96-question unified set, closed-book sets, BrowseComp-style research |
| Repair fixtures | [`repair/`](repair/README.md) | Agentic bug fixing in Python, C++, JavaScript and Rust |
| Historical results | [`results/`](results/README.md) | Past observations, with their caveats |

## Quick start

1. **Start an OpenAI-compatible server.** For example:

   ```powershell
   llama-server -m model.gguf -c 32768 --port 8080
   ```

2. **Run a QA suite.** The direct-HTTP runners ask for the port if you omit it:

   ```powershell
   cd qa/open-ended
   python run_suite.py --port 8080 --label trial-1
   ```

   Or from a closed-book folder:

   ```powershell
   cd qa/closed-book/easy-mixed-12
   python run_closed_book.py --port 8080
   ```

   Harness-driven and cloud-API suites use their own configuration instead
   (see [Connecting to a model](docs/CONNECTING.md)).

3. **Read the results.** Each run writes a result JSON plus one formatted
   Markdown file per question under `reasoning/`. Progress, a running score
   and a final score table are printed to the terminal.

## Requirements

- Python 3.10+ for all Python runners. The direct-HTTP runners use the standard
  library only; the optional web MCP server and the BrowseComp cloud-API runner
  need third-party packages (`requests`, `mcp`, `ddgs`).
- An OpenAI-compatible chat-completions endpoint on your own machine or a
  provider you control.
- For repair fixtures: a coding-agent harness that can work in a directory and
  call your endpoint. See [`repair/README.md`](repair/README.md).

## Key properties

- **No hardcoded endpoints in the direct-HTTP runners.** You supply the port
  interactively or with `--port`; no API keys are stored in this repository.
  The optional BrowseComp cloud-API runner (`qa/browsecomp/hard-10/`) is the
  exception: its endpoint and key-file path are fixed constants for the
  recorded run.
- **Standalone suites.** Each suite folder contains everything needed to run
  it, including its own question file and runner.
- **Reasoning is kept.** If your server returns `reasoning_content`, it is
  saved in the per-question Markdown files inside a fenced code block
  (trailing whitespace is trimmed).
- **Honest failure modes.** Missing rows mean `NOT RUN`. Single runs are not
  presented as robust statistics. Known scorer issues are documented rather
  than hidden.

## Documentation

- [Connecting to a model](docs/CONNECTING.md)
- [Methodology and reproducibility](docs/METHODOLOGY.md)
- [QA suites](qa/README.md)
- [Repair fixtures](repair/README.md) and [their security notes](repair/SECURITY.md)
- [BrowseComp-style research sets](qa/browsecomp/README.md)
- [Historical results and caveats](results/README.md)
- [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Security policy](SECURITY.md)

## License

Apache License 2.0. See [LICENSE](LICENSE).
