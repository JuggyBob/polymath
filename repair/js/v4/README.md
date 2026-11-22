# Repair fixture v4 (difficulty 9.5/10)

Domain: async iterators, streams, WeakMap caches, module-cycle-like lazy
initialization, event ordering, closure scope and a lookup performance
contract.

The task package lives in `task/`. It contains sixteen planted bugs. None of
the source lines are annotated, and **all visible tests pass on the starting
code** — the agent receives zero feedback from the visible suite. Hidden tests
carry the signal.

## Scoring

```sh
node <REPO>\repair\js\score_js.js \
  --fixture <REPO>\repair\js\v4 \
  --solution <path-to-solution-copy-of-task> \
  --out <report.json>
```

- Visible checks: 28 (all pass on pristine)
- Hidden checks: 40 (names prefixed `test_h_`)
- Planted bugs: 16
- Performance contract: 100,000 lookups over a 10,000-entry index in < 2 s
- Scope trap: deferred callbacks in `schedule()` capture a shared loop index
