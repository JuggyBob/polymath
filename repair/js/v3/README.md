# Repair fixture v3 (difficulty 8/10)

Domain: prototypes, `this` binding, generators, and aliasing / reference
semantics.

The task package lives in `task/`. It contains twelve planted bugs, each
marked with a `BUG` comment in the source. Several visible tests fail on the
starting code, so the agent gets direct feedback about what is broken.

## Scoring

```sh
node <REPO>\repair\js\score_js.js \
  --fixture <REPO>\repair\js\v3 \
  --solution <path-to-solution-copy-of-task> \
  --out <report.json>
```

The scorer runs the first `test_*.js` file in `task/tests` against both the
pristine copy and the candidate, then runs `_grader/hidden_tests/test_hidden.js`
against the candidate. It requires the test files to be byte-identical to the
pristine ones and applies a zero-regression gate.

- Visible checks: 16
- Hidden checks: 27
- Planted bugs: 12
