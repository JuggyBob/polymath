# Inventory service

A tiny standard-library inventory service used by the reporting CLI.

- `inventory/models.py` - `Item`
- `inventory/store.py` - `Store` (add, get, all, list_page, search)
- `inventory/report.py` - totals and category summaries

## Run the tests

```
python -m unittest discover -s tests -v
```

or:

```
run-tests.cmd
```

## Task

Four tests fail. Fix the implementation so the whole suite passes, following the
contracts in `AGENTS.md`. Do not edit the tests.
