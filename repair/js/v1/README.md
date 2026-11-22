# Repair fixture v1 — array/object utilities

Difficulty target: 5/10 (baseline hidden pass ratio 0.5).

Seven planted behavioural bugs across `sum`, `average`, `unique`, `chunk`,
`groupBy`, `frequency` and `clamp`. The traps include sparse arrays, `NaN`
handling, `Array.prototype.sort`'s default lexicographic order, mutating the
caller's array while iterating, shared module state, loose `==` equality and
`-0` normalisation. `flatten` is intentionally correct.

The module is CommonJS and has no dependencies. All contracts are documented
in `task/AGENTS.md`. Visible tests (`task/tests/test_visible.js`) show failures
on the buggy version. Hidden tests live in `_grader/hidden_tests/test_hidden.js`
and are applied by the scorer over a copy of the candidate solution.

Scoring from `<REPO>\js`:

```
node ..\score_js.js --fixture v1 --solution <candidate-dir> --out <report.json>
```
