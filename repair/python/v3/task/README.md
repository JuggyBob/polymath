# Job scheduler — repair fixture v3

A small in-memory scheduler used by a worker CLI. Standard library only.

- `scheduler/models.py` — `Job`
- `scheduler/core.py` — `Scheduler`
- `scheduler/metrics.py` — reporting helpers

## Run the tests

```
python -m unittest discover -s tests -v
```

## Task

Fix the implementation so both the visible and hidden tests pass, following the
contracts in `AGENTS.md`. **Do not edit the tests.**

The visible suite has failures, but it does not cover every contract. Several
bugs only appear after a **sequence of operations**, so test more than one call.

## Scoring

```
(Grading is run by the harness outside this workspace.)
```

Hidden tests live outside the agent workspace and are injected at grading time.
A zero-regression gate applies: breaking any currently passing test scores zero.
