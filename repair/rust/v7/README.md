# rust / v7 — MiniVM repair fixture

Spec-free, cross-cutting, long-horizon Rust repair benchmark.

- `task/` — the agent workspace: broken implementation, examples and visible
  tests. This is the only directory exposed to the agent.
- `_golden/src/` — the correct reference implementation. Never exposed to the
  agent. `_golden/examples/` holds the same canonical examples.
- `_grader/pristine/` — byte-identical copy of `task/`.
- `_grader/hidden_tests/test_hidden.rs` — hidden acceptance tests.
- `score_v7.py` — scorer with separate correctness and performance blocks.

## Scoring

```
python score_v7.py --fixture <REPO>/repair/rust/v7 --solution <path> --lang rust --out <path>
```

Test programs print `TEST <name> PASS|FAIL` and `PERF <name> <ms> PASS|FAIL`.
Every perf test runs exactly three times; the report records all three times
and the median. A perf failure lowers the performance score but never sets
`score_zero`. Only correctness regressions (including hidden-only regressions
against the pristine hidden baseline), test tampering, removed functional
files, public-API changes or compile failures set `score_zero`. The report also
records `public_api_intact`, `files_removed` and wall-clock timing.

Rust perf limits (median): `perf_print` 60 ms, `perf_disasm` 50 ms,
`perf_snapshot` 60 ms. These are at least 3x the golden reference's measured
time on the reference machine.

## Caveats

- Failures can be masked by earlier faults. New failures after a fix are
  expected and are part of the task. The task README says so explicitly.
- The canonical `examples/` are the only visible specification. A documented
  majority fail on the pristine source; the rest pass.
- Hidden tests are injected at grading time and are never present in `task/`.
- No build tool is used: each example and test driver is compiled directly
  with `rustc --edition 2021 -O`.

Visible fail expectation on the pristine source: 37 of 45 examples fail
(measured with rustc 1.100.0, `--edition 2021 -O`).
