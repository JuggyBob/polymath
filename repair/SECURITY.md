# Security notes for the repair fixtures

These fixtures are **local regression tools**, not a secure grading service.
This file records known weaknesses so nobody mistakes a score for a hardened
evaluation.

## Threat model

The solver is a local coding agent you control. It is not assumed to be
adversarial. If you need to evaluate untrusted agents, run the grader in a
fresh container/VM with no network and mount only the `run-*` directory.

## Known gaps (from independent audit, 2026-11-22)

| ID | Gap | Impact |
|---|---|---|
| H1 | A root `unittest.py` shadow can hijack the Python grader and suppress failures with `score_zero: false`; `sitecustomize.py` and sourceless `.pyc` were NOT effective in executable tests on Python 3.11.9. Only `tests/` is hashed and added files are not gated by all scorers | A cheating solution can alter grading |
| H2 | v2–v5 `public_api_present()` imports candidate packages inside the grader process | Candidate code runs with grader privileges and can reach hidden tests |
| H3 | Some task READMEs named the `_grader` path; removed from `task/` but still
present in a few solver `run-*` copies | Hidden tests could be read from disk if the agent had filesystem access |
| H4 | `score_zero` can stay false despite hidden failures or a crashed test process | Misleading zero/non-zero verdict |
| H5 | Some v5 hidden tests use private attributes (`_results`, `_queue`, `_closed`) not exposed by visible tests | Honest solutions may be failed |
| H6 | v6 `examples/` files are not hash-checked | A solver can alter the examples used as specification |
| H9 | v6 visible and performance passes are not required for a non-zero score | Partial solutions can score |

## Additional gaps found in the C++ / JS / Rust fixtures

| ID | Gap | Impact |
|---|---|---|
| C1 | Zero-regression gate ignores hidden failures in python, cpp, js and all v6 scorers; `score_rust.py` has a partial gate that only catches hidden tests which passed on pristine | Stored results show hidden failures with `score_zero: false` |
| C2 | No output-integrity check in cpp/js/rust/v6: invented or duplicated `TEST ... PASS` lines inflate `passed`; Python unittest scorers ignore such lines but an added fake test inflates the top-level scorer | A solver can inflate its passed count |
| C3 | The original C++ v5 solver workspace shipped `test_hidden.obj`, making all 49 hidden test names recoverable | Already excluded from this staging copy; binaries are not published |
| H1 | JS v6 visible tests read mutable `examples/*.expected`; only `tests/` is hashed | Tamper surface |
| H2 | v6 scorer never checks frozen C++ headers | Tamper surface |
| H3 | Toolchain paths are now environment-driven (`HARNESS_PYTHON`, `HARNESS_RUSTC`, `HARNESS_NODE`, `HARNESS_VCVARS`) with sensible defaults; configure them before scoring | Not portable without setup |
| H4 | `score_v6.py` ignores the run exit code: a process exiting 3 produced `compile: true`, 0 passed and `score_zero: false` | Compile failures can be misread |
| H5 | Rust v5 enforces a 20 ms hot-loop / 40 ms aggregate budget against a documented 2 s budget. The earlier claim that a correct C++ v6 solution fails perf under `/Od` was NOT reproduced: `_golden` passed both (3.27 ms, 15.26 ms) | Possible false failures on correct Rust solutions |

`score_rust.py` is the reference implementation for the hidden-failure
regression gate. Backporting it to the other three languages, adding a TEST
name manifest and hashing `examples/` and headers are the highest-value fixes.

## Mitigations you can apply today

- Run the agent with **no access** to `_grader/`, the parent fixture directory
  or this repository's answer keys.
- Grade in a fresh copy of `task/`, never in the directory the agent used.
- Read `hidden.failed`, `regressions`, `tests_modified`, `tests_added`,
  `files_removed` and the test process exit code — do not rely on `score_zero`.
- Compare the `task/` tree hash before and after the run.
- For untrusted agents, add a sandbox and an allow-list of files the solver may
  create.

None of these gaps affect the **fixture code**: source, tests and examples
are byte-identical between `task/` and `_grader/pristine/` in all v2-v6
fixtures. README files differ in six fixtures (`python/v3`, `python/v4`,
`python/v5`, `cpp/v3`, `js/v1`, `js/v2`) and `js/v5/task/` has two extra files
(`AGENTS.md`, `README.md`). Planted bugs are real and covered by the hidden
tests; `_golden` is a genuine fixed solution.

## Verified scorer behavior (2026-11-22 executable tests)

- The Craft scorer now returns **14/14** for a document with `w:b`, `w:i`,
  `w:bCs`, `w:iCs` and `w:sz=36`; both advertised fixes work.
- The Python v6 and JS v6 visible suites work once the shipped `.expected`
  files are present, and the zero-regression gate fires on tampering.
- Operators must read `hidden.failed`, `regressions`, added/removed files and
  the raw test-process exit code. `score_zero` alone is not authoritative.
- JS and Rust do not ship a `_grader/score.py`; use `score_js.js` / `score_v6.py`
  and `score_rust.py` / `score_v6.py`. The top-level Python `score.py` has no
  `score_zero`, `total` or `regressions` field.
