# LFM2.5 repair results — measured, with caveats

Dates: 2026-11-20 (fixture v5) and 2026-11-24 (fixture v4, plus cleanup).
All numbers below come from runs performed on the author's machine. Nothing in
this page is a published benchmark result and nothing here is vendor-reported.
Each fixture was attempted at most once; there are no repeats, no confidence
intervals and no cross-machine checks. A row that did not complete is marked
`NOT RUN` and is not estimated. Failure lists are kept in full.

Provenance of comparison figures: Qwen numbers are earlier locally measured
references recorded in prior reports on the same machine, not vendor claims.
The model-under-test figures are measured in the runs described here. Model
reasoning quoted in a separate section is the model's own account, not verified
measurement.

## Model and serving setup

| Item | Value |
|---|---|
| Model under test | `lfm2.5-24b-a2b` |
| Hermes alias | `lfm` |
| Weights (local file) | `LFM2.5-24B-A2B-UD-Q3_K_XL.gguf`, 10,947,100,928 bytes |
| Orchestration model | `opencode-go/hy4-flash-free#high` |
| Serving engine | Strata (`strata`), OpenAI-compatible server |
| Trial server config | campaign-only copy of a quantized `q3_k_m`, 65,536-context config |
| Context | 65,536 |
| KV / cache flags | `--max-context 65536 --kv-whole --conversation-cache-mib auto` |
| Client | Hermes, `--yolo --reasoning none` |
| Hardware / OS | Windows, RX 7600 XT, 31.11 GB total physical RAM |

Health evidence at the v5 load: `loaded:true` after 25.2 s of polling; response
`{"status":"ok","max_context":65536,"model":"lfm2.5-24b-a2b","images":false,"api_key":false,"image_generation":false,"api_monitor":false,"loaded":true,"service":"strata"}`.
Engine log: loaded in 27.0 s, 2,432 of 2,432 routed experts in VRAM (9.5 GiB),
8 CPU threads, conversation cache sized from free RAM to 4,096 MiB for up to 4
parked conversations. Health was rechecked during and after the run with zero
consecutive failures; the server was never restarted mid-fixture. The trial
server used one campaign-only port; the daily-driver server was never started
or touched, and its config, engine, expert profile and weights stayed unchanged.

## Summary of attempts

| Fixture | Date | Status | Score | `score_zero` |
|---|---|---|---|---|
| v5 `coord-hard` (Python) | 2026-11-20 | MEASURED | 70/80 raw | true |
| v5 (C++) | 2026-11-20 | **NOT RUN** | none | none |
| v5 (JavaScript) | 2026-11-20 | **NOT RUN** | none | none |
| v5 (Rust) | 2026-11-20 | **NOT RUN** | none | none |
| v4 `telemetry-hard` (Python) | 2026-11-24 | MEASURED | 43/70 | false |

## v5 `coord-hard` (Python) — measured

**Date:** 2026-11-20. Wall clock 06:52:33–07:10:53 local (05:52:33–06:10:53 UTC).

**Harness.** Hermes invoked with `-z "<prompt>" -m lfm --yolo --reasoning none`
in a copied candidate workspace. The harness never touched `tests/`. The v5
prompt was the task-brief base prompt plus the Python v5 addendum, pointed at
`README.md` and the examples. The Qwen reference run used a different prompt
(pointed at `AGENTS.md`), so this is a harness-recorded comparison, not a
prompt-identical A/B. The Python scorer has no separate compile stage
(`compile` = N/A); both suites executed.

### Run control — two attempts

- **Attempt 1, stopped early, no edits.** A wrapper flag of
  `REPEATED_ACTION_LOOP` at 106.3 s (terminal call count 6) was a false
  positive: the wrapper re-counted the same historical log line on every 15 s
  poll. The transcript shows one terminal call (875 chars) and two API calls.
  The real event was a filesystem-wide `find / -type d -name 'coord'` scan that
  hung; the wrapper stopped Hermes before its own 180 s terminal timeout could
  recover. No source file was modified.
- **Attempt 2, the measured run.** The same scan hung until the 180 s tool
  timeout at 06:52:45, then continued. 71 API calls; four source modules
  edited. From API call #56 to #70 (07:09:24–07:10:52) the same failing test
  command was re-run at least 15 times, each returning the same
  `asyncio.run(drain())` traceback in about 0.5 s. Context compression failed
  three times (`summary_empty_content_failure`), followed by
  `HTTP 400: request exceeds the context window: prompt (65858 tokens) leaves no room to answer in the context (65536)`.
  Hermes auto-reset the session. There was no clean final answer. Wall clock
  1071.2 s (attached monitor) / 1096.2 s (gateway `time=`). Hard caps of 3600 s
  (primary) and 1800 s (monitor) were not reached; the stop came from Hermes'
  context-overflow failure, not from the harness.

### Exact score (measured)

| Block | Passed | Failed | Total | Returncode |
|---|---:|---:|---:|---:|
| Visible | 24 | 1 | 25 | 1 |
| Hidden | 46 | 9 | 55 | 1 |
| **Total** | **70** | **10** | **80** | — |

- `compile`: N/A (Python scorer has no separate compile stage).
- `score_zero`: **true**. A visible-test regression (`test_drain_one`) was
  introduced; the harness zeroes the result despite 70/80 raw passes. This is
  the headline outcome.
- Failed visible: `test_drain_one`.
- Failed hidden: `test_h_api_astream_closes`, `test_h_api_astream_task_done`,
  `test_h_api_config_no_self_retention`, `test_h_cache_gc_drops_entry`,
  `test_h_desc_per_instance`, `test_h_desc_slotted`, `test_h_queue_drain_full`,
  `test_h_queue_task_done_over`, `test_h_queue_track_weak_gc`.
- `baseline_visible_passed`: 25.

### Anti-cheat fields (from the scorer JSON)

| Field | Measured value |
|---|---|
| `regressions` | `["test_drain_one"]` |
| `tests_modified` | `[]` |
| `tests_removed` | `[]` |
| `tests_added` | `[]` |
| `files_removed` | `[]` |
| `public_api_intact` | `true` |
| `score_zero` | `true` |

No test, header or public-API tampering. The only integrity failure is the
self-inflicted visible regression.

### RAM and commit (measured)

| Point in campaign | Free physical | Used physical | Commit |
|---|---:|---:|---|
| Before Hermes (baseline) | 16.74 GB | 14.38 GB | 24,667 MB / 58,485 MB limit |
| After Hermes + scoring | 19.10 GB | 12.01 GB | not re-sampled |

The commit figure after scoring was not re-sampled because the shell tool
became unavailable. Total physical RAM was 31.11 GB throughout; pagefile at
baseline was 26,624 MB allocated, 0 MB in use. The trial server was left
running. Baseline source commit was `c77572806996349b49995e4f98d41b5294d36a21`;
the post-run commit check could not be completed after the shell tool stopped
responding, and no git operation was performed by this campaign. The harness
directory is not a git repository, so no harness commit is claimed.

### Comparison (all locally measured, prior references for Qwen)

| Metric | Pristine reference | Fully-fixed reference | Qwen3.6-35B-A3B | LFM2.5-24B-A2B |
|---|---:|---:|---:|---:|
| Visible passed | 25/25 | 25/25 | 25/25 | 24/25 |
| Hidden passed | 23/55 | 55/55 | 51/55 | 46/55 |
| Total passed | — | 80/80 | 76/80 | 70/80 |
| `score_zero` | — | false | false | **true** |
| Wall clock | — | — | 161.7 s | 1071.2 s |

LFM scored 6 raw passes below Qwen and, unlike Qwen, introduced a visible
regression, so its effective score is zero. It also took about 6.6× the wall
clock and ended in a context-overflow failure instead of a normal finish. The
prompts differed, so this is not a controlled A/B.

### Model output — the model's own account, not measured fact

The model produced no substantive final reasoning. Captured Hermes stdout
contained only the failure notice that the conversation had grown too long for
`lfm2.5-24b-a2b` to read and could not be shrunk enough automatically, followed
by a session auto-reset notice. Its observable actions, taken from the agent log
and the resulting diff:

- First action: a terminal command producing 875 chars (directory listing),
  then the `find /` scan that hung to the 180 s tool timeout.
- Edited `coord/context.py` (moved to `contextvars.ContextVar` with
  `reset(token)`, per-instance `values`, `.id` from `request_id`),
  `coord/cache.py` (weakref keys, full `clear()`, `__set_name__` uses the real
  name), `coord/queue.py` (FIFO `pop(0)`, `join()` on `unfinished_tasks`,
  weakref workers, `drain()` with `task_done()`), and `coord/api.py`
  (exception chaining with `from exc`, `KeyError` in `result()`, unsorted
  `failed_ids()`, simplified `total()`, `astream` sets `_closed`).
- In `drain()` it left both an in-loop `queue.task_done()` and an unconditional
  `finally: queue.task_done()`, and also wrote `queue._closed = True`. This
  plausibly explains the measured `test_drain_one` regression and several
  hidden queue failures. That attribution is static analysis of the diff and
  is unconfirmed beyond the score.
- It then re-ran the same failing test command (API #56–#70) without changing
  it until context overflow ended the turn.

Honest summary: the model made meaningful, largely correct edits (46/55 hidden
pass, better than the pristine baseline's 23/55), but looped on a failing test,
broke one visible test, and never delivered a final answer. The harness scores
the result zero.

## v4 `telemetry-hard` (Python) — measured

**Date:** 2026-11-24.

The prompt was identical to the measured Qwen v4 run and used the same
`--yolo --reasoning none` flags. The trial server used a campaign-only config
copy under a run guard; preflight passed and the campaign server was stopped
after scoring. Server ready 14:06:11; Hermes 14:06:11 → 14:16:45 (**634.2 s**,
exit 2, not capped); scorer done 14:16:49.

Hermes usage: **142 API calls, 6,554,893 input tokens, 9,254 output tokens**,
3 compression calls, `failed: true`, with failure text that the conversation
had grown too long for `lfm2.5-24b-a2b` to read and Hermes could not shrink it
enough automatically.

| | LFM v4 | Qwen v4 |
|---|---:|---:|
| Visible | 28/28 | 28/28 |
| Hidden | 15/42 | 36/42 |
| **Total** | **43/70 (61.4%)** | **64/70 (91.4%)** |
| `score_zero` | false | false |
| Regressions / test edits | none | none |

LFM failed the agreed cutoff: 21 fewer passes than Qwen overall and 15/42 vs
36/42 on hidden tests. `score_zero` is false and there were no regressions, so
the raw score is valid — it is simply much worse. A caretaker shell was
cancelled by an OpenCode server restart at about 14:20, but the campaign had
already finished and been scored at 14:16:49; the cancellation did not affect
the result, and all processes were gone when checked.

Evidence kept: score JSON, usage JSON and a master log from this run. Per the
standing rule, the LFM weights, trial config and log, launcher, install
manifest, desktop shortcut and Hermes alias were deleted; the trial folder was
removed after evidence was copied. By explicit choice, the tokenizer pack and
the directory referenced by the old launcher were left in place. No promotion
is claimed or implied.

## v5 C++, JavaScript and Rust — NOT RUN

All three were blocked by the same harness tooling failure on 2026-11-20. The
campaign is sequential: Python v5 ran first and was scored, then the harness
`shell` tool stopped working — every command, even a trivial date query,
returned `opencode-pty request timed out` immediately. This was confirmed with
foreground calls, background calls, alternate working directories and timeouts
up to 600 s. No alternate command executor was exposed to the subagent.

Consequently no workspace copy, Hermes launch, scorer invocation or evidence
capture was possible. **For each of C++, JavaScript and Rust there is no score,
no candidate, no timing and no process evidence.** Nothing in those three
reports should be read as an LFM2.5 measurement. They require a re-run in a
session with a working shell tool.

| Fixture | Status | Prepared before the outage | Prior Qwen reference (measured earlier) |
|---|---|---|---|
| C++ v5 | **NOT RUN** | prompt file (base prompt plus C++ v5 addendum), runner script with 3600 s hard cap, health checks and repeated-action/stall detection; intended scorer command written down; PowerShell wildcard bug fixed to `.Contains()` before this fixture | 63/65, `score_zero: false`; failures `test_h_sched_pending_and_completed`, `test_h_sched_run_all_twice` |
| JavaScript v5 | **NOT RUN** | scorer decision verified: fixture's own scorer is correct (hidden tests print `TEST <name> PASS|FAIL`, no `PERF` lines), not the v6 scorer; prompt file with base prompt only | 29/58, `score_zero: false` |
| Rust v5 | **NOT RUN** | prompt file with base prompt only; intended scorer command written down | 69/69, `score_zero: false`, no failed tests |

Environment state at the time of the block (last successful measurement): the
LFM trial server was left running with `loaded:true` at 65,536 context; no Qwen
server was started; physical RAM was 19.10 GB free / 12.01 GB used out of
31.11 GB total.

## Known C++ scorer defect (published fixture, separate from the LFM NOT RUN)

The v5 C++ scorer fails before grading either engine with
`NameError: name 'shutil' is not defined` at line 39: `copy_tree` calls
`shutil.copytree` but the module is never imported. It was reproduced manually
and fails identically for both engines compared in that earlier work. This is
a defect in the published fixture, not in either engine, and that C++ campaign's
score is `NOT RUN`.

The defect was fixed **in a trial copy of the scorer only**.
The patch adds a single missing `import shutil` and does not touch scoring
logic; the published fixture was left untouched. The patched copy was never
used to change any published score. This defect is unrelated to the LFM C++ v5
`NOT RUN` above, which was caused by the shell outage before any scoring could
start.

## Limits

- One measured run per completed fixture; the v5 Python run itself contains a
  stopped first attempt, but only attempt 2 was scored. No repeats, no
  statistics, no other hardware.
- The v5 Python comparison with Qwen is not prompt-identical.
- The v4 comparison is a single run against a previously recorded Qwen run.
- Three v5 fixtures and the earlier patched-scorer C++ campaign have no score
  at all; they are not estimated and are not counted as passes or failures.
- Model reasoning and diff attribution are reported as the model's account and
  static analysis, not as independent measurement.
- Nothing here is an official benchmark result, and no model promotion is
  claimed.
