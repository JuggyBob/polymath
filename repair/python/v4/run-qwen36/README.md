# Telemetry event log — repair fixture v4-hard

A small in-memory event log used by a reporting CLI. Standard library only.

Modules: `events`, `log`, `metrics`, `itertools_helpers`, `context`, `cache`, `format`.

## Run

```
python -m unittest discover -s tests -v
```

## Task

All visible tests pass. The implementation is still wrong. Fix it according to
`AGENTS.md`. Do not edit the tests. Do not add dependencies.

Several bugs require knowing that a function must be read-only, that a cache key
must identify the request, and that a decorator must preserve function metadata.
Read the worked examples in `AGENTS.md` carefully — some rules are given only by
example.

## Scoring

```
python <REPO>\repair\python\v4\_grader\score.py --solution <dir>
```

Hidden tests live outside the workspace and are injected only at grading time.
A zero-regression gate applies.
