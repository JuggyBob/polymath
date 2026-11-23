# MiniVM

This VM is broken in several ways. Hidden acceptance tests define correctness.
Run the examples to see the intended behaviour.

Failures may be masked by earlier faults. After a fix, re-run everything: new
failures are expected and are part of the task.

Do not change the example files. The visible tests and examples are the only
specification.

## Layout

- `src/` — the implementation (CommonJS modules, Node 18+).
- `examples/` — 45 Node drivers. Each imports `../src/index.js`, runs a
  program and writes its stdout; the matching `.expected` file holds the
  correct bytes.
- `tests/test_visible.js` — runs every example and the three timing checks.

## Running one example

From this directory:

```
node examples/prog01_arith.js
```

The process prints the program's stdout. Compare it with
`examples/prog01_arith.expected`.

## Running the visible suite

From this directory:

```
node tests/test_visible.js
```

Each example prints `TEST <name> PASS` or `TEST <name> FAIL`. Timing checks
print `PERF <name> <milliseconds> PASS|FAIL`, three lines per workload.
