# Repair task

A small in-memory inventory service. Some tests fail. Fix the code.

## Rules

- Do **not** modify anything under `tests/`. Those files are frozen.
- Do **not** remove or rename public functions, classes or arguments.
- Standard library only. Do not add dependencies.
- Keep the fixes small and local.

## Verifying

```
python -m unittest discover -s tests -v
```

or run `run-tests.cmd`.

## Contracts

### `Store.list_page(page, size=3)`

- `page` is **1-based**: page 1 is the first `size` items.
- `page < 1` or `size < 1` raises `ValueError`.
- A page past the end returns `[]`.
- The last page may be shorter than `size`.

### `Store.search(query)`

- Substring match against `Item.name`.
- Case-insensitive using Unicode case folding, so `"STRASSE"` matches `"Straße"` and `"CAFÉ"` matches `"Café"`.
- An empty query matches every item.

### `report.total_value_cents(items)`

- Returns the exact integer sum of `item.value_cents`.
- No rounding, no floats. `Item.value_cents == price_cents * quantity`.

## Notes

- The service is small; the failures are independent.
- There is at least one red herring in the code. Do not "optimize" things that are already correct.
