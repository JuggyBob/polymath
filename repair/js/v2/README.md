# Repair fixture v2 — promises and async

Difficulty target: 6.5/10 (baseline hidden pass ratio 0.65).

Nine planted behavioural bugs across `retry`, `withTimeout`, `mapLimit`,
`Emitter`, `debounce`, `memoizeAsync` and `promisePool`. Traps include an
off-by-one retry count, an unhandled rejection in `withTimeout`, result order
loss, `this` binding in emitter callbacks, `once` auto-removal and `off`
matching, microtask timing in `debounce`, caching a resolved value instead of
the in-flight promise, and a stale loop-variable closure in `promisePool`.

The module is CommonJS and has no dependencies. All contracts are documented
in `task/AGENTS.md`. Visible tests (`task/tests/test_visible.js`) show failures
on the buggy version; hidden tests are in `_grader/hidden_tests/test_hidden.js`.

Scoring from `<REPO>\js`:

```
node score_js.js --fixture v2 --solution <candidate-dir> --out <report.json>
```
