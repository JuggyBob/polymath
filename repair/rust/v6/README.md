# rust / v6 — MiniVM repair fixture

Spec-free, cross-cutting, long-horizon Rust repair benchmark.

- `task/` — the agent workspace: broken implementation, examples and tests.
- `_golden/src/` — the correct reference implementation. Never exposed to the agent.
- `_grader/pristine/` — byte-identical copy of `task/`.
- `_grader/hidden_tests/test_hidden.rs` — hidden acceptance tests.
- `score_v6.py` — copy of the generic scorer (run with `--lang rust`).

Correctness and performance are scored separately. Every perf test runs three
times and reports all three times plus the median. A perf failure never sets
`score_zero`; only correctness regressions, test tampering, public-API changes
or compile failures do.
