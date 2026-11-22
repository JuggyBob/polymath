# Order ledger — repair fixture v2

A slightly larger in-memory ledger used by a reporting CLI. Standard library only.

- `ledger/models.py` — `Order`
- `ledger/ledger.py` — `Ledger`
- `ledger/report.py` — reporting helpers

## Run the tests

```
python -m unittest discover -s tests -v
```

## Task

Fix the implementation so both the visible and hidden tests pass, following the
contracts in `AGENTS.md`. **Do not edit the tests.**

The visible suite has failures, but it does not cover every contract. Read `AGENTS.md`.

## Scoring

```
python score.py                       # runs on the current directory
python score.py --solution <dir>      # scores a candidate copy
```

Produces `score.json` with `visible` and `hidden` blocks, plus anti-cheat checks
(`tests_modified`, `files_removed`, `public_api_removed`).

A zero-regression gate applies: if a test that passes on the pristine fixture fails
after the repair, the task scores zero.
