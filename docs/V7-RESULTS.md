# v7 results — measured, with caveats

Date: 2026-11-22 to 2026-11-23. All numbers below are from runs performed on
the author's machine. Nothing here is a published benchmark result. A row that
did not complete is marked `CAPPED` or `NOT RUN` and is not estimated.

## Fixture validation (before model runs)

Every fixture was built and then audited twice by independent
`opencode-go/hy4-flash-free` subagents: a first audit that found genuine
defects, and a post-fix re-audit. All four passed 8/8 post-fix checks.

| Language | Golden visible | Golden hidden | Pristine visible FAIL | Golden perf medians (ms, print / disasm / snapshot) | Scorer probes |
|---|---:|---:|---:|---|---|
| Python | 45/45 | 49/49 | 28 | 136.19 / 5.84 / 6.30 | hidden regression, perf-only, file/API loss PASS |
| C++ | 45/45 | 49/49 | 32 | 7.86 / 1.39 / 0.23 (g++ -O2) | hidden regression, perf-only, file/API loss PASS |
| JavaScript | 45/45 | 49/49 | 31 | 16.82 / 1.13 / 2.82 | syntax failure, hidden regression, perf-only PASS |
| Rust | 45/45 | 49/49 | 37 | 6.47 / 3.89 / 0.37 | hidden regression, perf-only, file/API loss PASS |

Cross-language mechanical check: all 45 canonical example names and byte-exact
expected outputs are identical in `task/`, `_golden/` and `_grader/pristine/`
for all four languages; all 49 hidden names are present; the two scorer copies
in each fixture are byte-identical.

Defects found and fixed during auditing are listed in `docs/V7-AUDIT.md`.

## Qwen3.6-35B-A3B UD-Q3_K_M campaign (v7, hermes)

Model: the existing daily-driver Qwen setup, via an OpenAI-compatible server
and hermes with `--yolo --reasoning none`. The server used a campaign-only
config: 98,304 context, dynamic KV (no `--kv-whole`), no conversation cache,
2,048 MiB expert RAM budget, 2,048 MiB VRAM reserve, 4,096-token prompt batch.
The daily-driver config and all engine binaries were left unchanged.

One model was loaded at a time. `guard-model-load.ps1` passed before each load.
`guard-run.ps1` enforced an 80% commit ceiling throughout. Because the loaded
35B model itself holds roughly 12 GiB of physical RAM, the client-run free-RAM
trigger was lowered from 12 GiB to 4 GiB; the hard 80% commit ceiling, the
65% start ceiling and process-tree-only killing were unchanged. This deviation
is recorded in the local run plan.

| Language | Hermes outcome | Visible | Hidden | Perf | Wall time | Interpretation |
|---|---|---:|---:|---|---:|---|
| Python | completed (capped at 1800 s after work was done) | 45 pass / 0 fail | 47 pass / 2 fail | 6 pass / 0 fail | 1833.7 s | valid result |
| C++ | `CAPPED` at 3700 s | NOT RUN | NOT RUN | NOT RUN | 3700 s | agent was still debugging; no output file |
| JavaScript | `CAPPED` at 3700 s | NOT RUN | NOT RUN | NOT RUN | 3700 s | engine stalled late; no output file |
| Rust | `CAPPED` at 3700 s | NOT RUN | NOT RUN | NOT RUN | 3700 s | no output file |

### Python detail

- Hidden failures: `h_serial_full`, `h_str_concat_mixed`.
- `score_zero = false`, `regressions = []`.
- Hermes final message reported "All 45 tests PASS and all PERF tests PASS
  consistently", then listed fixes in `values.py`, `vm.py`, `snapshot.py` and
  `serialize.py`. The hidden-suite result above is the authoritative score.
- The run was stopped at the 1800 s hermes cap after scoring work had finished;
  the cap is a harness limit, not a model result.

### Why the other three did not complete

The wrapped engine intermittently returned an SSE stream with no
`finish_reason` and no `[DONE]` on long prompts, which hermes retried three
times. The problem was reproduced with direct HTTP requests: a fresh server
handled 3K–11K-token prompts correctly, but the engine degraded after failed
requests. Restarting the server before each run did not prevent late-stage
stalls in C++, JS and Rust. These are infrastructure failures. No score is
inferred for them.

## Comparison with v6

Qwen's earlier v6 campaign (recorded before this work) was:

| Language | v6 correct | v6 perf |
|---|---:|---:|
| Python | 108/108 | 1/3 |
| C++ | 64/64 | 0/2 |
| JavaScript | 42/73 | 4/4 |
| Rust | 27/38 | 2/4 |

v7 is not directly comparable to v6: the test counts, features and fault
structure all changed. The only like-for-like statement supported by this
work is that v7's hidden suite is substantially harder than v6's for the one
language that completed — Qwen passed 47/49 hidden v7 tests after a long agentic
run, while v7's pristine baseline passes far fewer.

## Inkling 2 Mini comparison

See `docs/V6-INKLING-COMPARISON.md`. The agentic v6 run did not complete; no
Inkling repair score is claimed.
