# Repair fixture v5 (JavaScript)

Target difficulty: 10/10. Runtime: Node v24.22.1. No third-party dependencies.

## Layout

```
v5/
  README.md                     this file (fixture metadata)
  task/                         the workspace handed to the repair agent
    AGENTS.md                   agent instructions (contains the scope trap)
    README.md                   normative behaviour contract, with worked examples
    src/*.js                    five CommonJS modules, 24 planted bugs, no annotations
    tests/test_visible.js       12 visible tests -- all pass on pristine (zero feedback)
  _grader/
    pristine/                   byte-identical copy of task/src + task/tests
    hidden_tests/test_hidden.js 46 hidden tests, names prefixed test_h_
```

## Domains covered

* event-loop semantics (timer vs microtask vs promise ordering)
* microtask/macrotask ordering and drain counts
* Proxy traps: `get`, `set`, `has`, `ownKeys`, `deleteProperty`,
  `getOwnPropertyDescriptor`
* WeakMap / identity-keyed caching (with a scope-red-herring shared store)
* async generators and async iteration, including `finally` cleanup on early close
* optimisation contract: `isPrime(n)` at O(sqrt(n)), inclusive sqrt boundary,
  edge cases (0, 1, negatives, 2^31+1), and 1,000,000 candidates under 2 s

## Scoring

```
node <REPO>\repair\js\score_js.js `
  --fixture <REPO>\repair\js\v5 `
  --solution <dir> `
  --out <json>
```

The scorer copies pristine and solution to a temp dir, runs the visible test
against both, swaps in the hidden test against the solution, checks that the
test files are unmodified, and applies a zero-regression gate.

The hidden performance test bounds its own wall time so an O(n) "optimisation"
fails quickly instead of hanging. It checks both the elapsed time and the exact
prime count below 1,000,000 (78498), so a wrong (exclusive) square-root
boundary also fails.
