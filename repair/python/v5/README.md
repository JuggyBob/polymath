# Repair fixture v5-hard — async job coordinator

Standard-library-only Python repair fixture. Domain: an async/concurrent job
coordinator with request-scoped contexts, a weakref value cache, an async task
queue and a public facade.

Layout:

- `task/` — the workspace given to the solver. All visible tests pass on it,
  but 20+ planted bugs remain. `task/AGENTS.md` states the contracts.
- `_grader/pristine/` — an untouched copy of `task/`.
- `_grader/hidden_tests/test_hidden.py` — 55 hidden contract tests, injected
  only at grading time.
- `_grader/score.py` — the scorer.

Run the visible suite:

```
python -m unittest discover -s <REPO>\repair\python\v5\task\tests -v
```

Grade a candidate:

```
python <REPO>\repair\python\v5\_grader\score.py --solution <dir> --out <file.json>
```

A zero-regression gate applies: a candidate that breaks a baseline-passing
visible test scores zero. No third-party dependencies.
