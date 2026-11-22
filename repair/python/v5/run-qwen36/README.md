# Async job coordinator — repair fixture v5-hard

A small async job coordinator with request-scoped context, a weakref value
cache, an async task queue and a public facade. Standard library only.

Modules: `coord.context`, `coord.cache`, `coord.queue`, `coord.api`.

## Run

```
python -m unittest discover -s tests -v
```

## Task

All visible tests pass. The implementation is still wrong. Fix it according to
`AGENTS.md`. Do not edit the tests. Do not add dependencies.

Several bugs require knowing that a context must be task-local, that a weak
cache must let keys be collected, that an async generator must mark items done
even on early close, and that an exception must be chained with `from`. Read
the worked examples in `AGENTS.md` carefully — some rules are given only by
example.

## Scoring

```
python <REPO>\repair\python\v5\_grader\score.py --solution <dir>
```

Hidden tests live outside the workspace and are injected only at grading time.
A zero-regression gate applies.
