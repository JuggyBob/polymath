# Repair fixtures

Agentic code-repair tasks in four languages. Each version gives the solver a
`task/` directory with planted bugs whose contracts are still violated while
some checks pass. Early fixtures (v1-v3 in Python, C++, Rust and JavaScript,
plus the Python v1 inventory service in `template/`) ship visible tests that
FAIL on the pristine source as feedback. The v4/v5 adversarial fixtures ship
visible tests that all pass on pristine, but the v6 Python and JavaScript
fixtures do give visible feedback (the buggy source fails 52 and 4 visible
checks respectively). The agent must read the contract and fix the code.

| Folder | Language | Versions | Scorer |
|---|---|---|---|
| `python/` | Python 3 (stdlib only) | v1 (`template/`) and v2–v6 | `score.py`, `score_v6.py`, `_grader/score.py` |
| `cpp/` | C++20 | v1–v6 | `score_cpp.py`, `score_v6.py`, `_grader/score.py` |
| `js/` | JavaScript / Node | v1–v6 | `score_js.js` (v1–v5), `score_v6.py` (v6) |
| `rust/` | Rust (stdlib only) | v1–v6 | `score_rust.py`, `score_v6.py` |

### v7 — hard cascading-fault edition

`v7/` exists in all four languages and is built from one canonical manifest,
[`v7-tests.json`](v7-tests.json). It is deliberately harder than v1–v6: bugs
are masked by prerequisite faults, so new failures appear only after earlier
ones are fixed; the VM gains deterministic fibers and a checksummed snapshot
format; and there are 45 visible examples, 49 hidden tests and three performance
gates per language.
See [`docs/V7-DESIGN.md`](../docs/V7-DESIGN.md) for the shared contract and
[`docs/V7-RESULTS.md`](../docs/V7-RESULTS.md) for measured results. v7
intentionally overrides v6 design rule R5 (no masked bugs); this is documented
in the v7 design doc.

Version summary (Python): v1 inventory service (in `template/`), v2 order ledger, v3 job scheduler,
v4 telemetry/aggregation, v5 async coordinator + weakref cache, v6 bytecode VM,
v7 MiniVM with masked cascading faults, deterministic fibers and snapshots.

## Layout of one version

```
v5/
├── task/                  # the ONLY directory the solver sees
│   ├── AGENTS.md          # written contract (or README.md in v6)
│   └── ...                # source + visible tests
├── _grader/
│   ├── pristine/          # regression baseline (README may differ)
│   ├── hidden_tests/      # injected only at grading time
│   └── score.py           # scorer
└── run-<label>/           # solver's copy of task/ (you create this)
```

## Setup — as easy as possible

Run all commands below from the repository root.

1. **Copy the task.** Never let the agent work in `task/` itself.

   ```powershell
   Copy-Item -Recurse repair\python\v5\task repair\python\v5\run-my-model
   ```

2. **Point your agent harness at your model.** These fixtures do not call the
   model directly. Configure your harness (Hermes, Claude Code, Codex, etc.)
   with an OpenAI-compatible endpoint of your choice. For example, with a local
   server on port 8080, set the harness provider/base URL to
   `http://127.0.0.1:8080/v1`.

3. **Run the agent in the copied directory** with a prompt that tells it to fix
   the bugs according to `AGENTS.md`, keep fixes local, and not modify `tests/`.
   Example:

   ```powershell
   cd repair\python\v5\run-my-model
   hermes -z "Fix the bugs in this repository according to AGENTS.md. Do not modify anything under tests/. Standard library only." --yolo --reasoning none
   ```

4. **Run the visible suite** (optional, quick sanity check):

   ```powershell
   python -m unittest discover -s tests -v
   ```

5. **Grade the copy from the fixture root**, not from inside the run
   directory:

   ```powershell
   cd ..\..\..\..
   python repair\python\v5\_grader\score.py --solution python\v5\run-my-model --out python\v5\my-score.json
   ```

   The scorer injects hidden tests, checks for visible-test regressions and
   tampering, and writes a JSON with `visible`, `hidden`, `total`,
   `regressions`, `tests_modified`, `tests_added`, `tests_removed`,
   `files_removed` and `public_api_intact`.

## Requirements by language

- Python: 3.10+, standard library only.
- C++: C++20 compiler (`clang++` or MSVC); tests compile locally.
- JavaScript: Node 22+.
- Rust: stable toolchain, standard library only.

No network access is needed for grading.

## Important limitations — read before trusting a score

These fixtures were built for local model selection, not as a hardened
competitive benchmark. An independent audit found the following gaps. They are
disclosed here rather than hidden:

1. **Anti-cheat is not sandboxed.** A solver that writes `sitecustomize.py`,
   replaces `unittest.py`, or adds sourceless `.pyc` files can interfere with
   grading. Only `tests/` is hashed; added files are not gated by all scorers.
2. **The grader imports candidate code in-process** for the public-API check in
   v2–v5, which means candidate code can execute with grader privileges.
3. **Some task READMEs historically disclosed the grader path.** The grader is
   never needed by the solver; do not give the agent access to `_grader/` or
   any directory outside its `run-*` copy.
4. **`score_zero` does not always reflect hidden failures or a crashed test
   process.** Treat the `hidden.failed` list and process exit code as the
   authoritative signal, not just the `score_zero` flag.
5. **Some hidden tests reference private attributes** an honest solution might
   legitimately rename. A miss on those is not proof of a wrong fix.
6. **v6 `examples/` files are not hash-checked.** A solver could modify them.

For a fair comparison, give every model the same prompt, the same harness
version, the same `task/` bytes and no access to `_grader/` or this README's
answer details. Keep the run directories for audit.
