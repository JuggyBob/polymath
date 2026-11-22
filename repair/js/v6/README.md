# MiniVM v6 — JavaScript repair fixture

Spec-free, cross-cutting repair benchmark. The agent sees only `task/`.
The examples in `task/examples/` (with `.expected` stdout) are the visible
specification; there is no separate contract document and no `AGENTS.md`.

## Layout

- `task/` — agent workspace (broken implementation + examples + visible test).
- `_golden/` — complete correct implementation; used only as a scoring target.
- `_grader/pristine/` — byte-identical copy of `task/`.
- `_grader/hidden_tests/test_hidden.js` — hidden acceptance tests.
- `score_v6.py` — generic v6 scorer (use `--lang js`).

## Example coverage

All hidden acceptance behaviours now have a visible example. Examples use the
same semantic rule with different inputs from the hidden tests, so every
non-`distinct` example passes on the broken tree while the corresponding hidden
test still detects the defect. Example files may be:

- a language program (default), run with `vm.run(source)`;
- `// @api` — a JavaScript snippet using the public API;
- `// @api-async` — an awaitable JavaScript snippet;
- `// @api-perf` — a snippet that calls the injected `perf()` helper.

The four `distinct` examples are the documented exception: they fail on the
broken build and pass on the golden reference.

## Scoring

```
python score_v6.py --fixture <this dir> --solution <dir to score> --lang js --out <json>
```

Correctness comes from `TEST` lines; performance from `PERF` lines (three runs
per perf test). A performance failure never sets `score_zero`.
