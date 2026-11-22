# Repair task: order ledger

A small in-memory order ledger used by a reporting CLI. **Some tests fail. Fix the code.**

## Rules

- Do **not** modify anything under `tests/`. Those files are frozen.
- Do **not** remove or rename public functions, classes or arguments.
- Standard library only. Do not add dependencies.
- Keep fixes small and local.
- Do **not** change the data model's public fields.

## Verifying

```
python -m unittest discover -s tests -v
```

Hidden tests are not visible to you. Passing the visible suite is necessary but **not
sufficient** — read the contracts below carefully.

## Contracts

### `Order` (in `ledger/models.py`)

- `Order(order_id, ts, side, qty, price_cents, status="open")`
- `notional_cents` = `qty * price_cents` (exact integer).
- `age_seconds(now)` = `now - ts`. A timestamp in the future gives a **negative** age.

### `Ledger.add(order)` / `Ledger.get(order_id)` / `Ledger.all()`

- `add` raises `ValueError` on duplicate id.
- `get` raises `KeyError` for a missing id.
- `all()` returns a copy; mutating it must not affect the ledger.

### `Ledger.open_orders()` / `Ledger.fill(order_id)` / `Ledger.cancel(order_id)`

- `open_orders()` returns only orders whose status starts with `"open"`.
- `fill` sets status to `"filled"`; `cancel` sets it to `"cancelled"`.
- Both raise `KeyError` for a missing id.
- Calling `fill` on an already-filled order is a no-op (idempotent).
- Calling `cancel` on a filled order raises `ValueError`.

### `Ledger.total_notional_cents(status=None)`

- Exact integer sum of `notional_cents` for all orders, or only those whose `status`
  equals `status` when given.
- Returns `0` for no matches.

### `Ledger.slice_orders(start, end)`

- `start` and `end` are 0-based, `end` exclusive, and use Python slicing semantics:
  negative indices count from the end, out-of-range indices clamp, and a reversed
  range gives `[]`.
- Returns a list (copy).

### `Ledger.search(query)`

- Substring match against `Order.note`, **Unicode case folded**.
- `"STRASSE"` matches `"Straße"`; `"CAFÉ"` matches `"Café"`.
- An empty query matches every order.

### `Ledger.oldest(n=1, now=0)`

- Returns the `n` orders with the **smallest** `ts` (oldest first).
- `n < 0` raises `ValueError`; `n == 0` returns `[]`.
- Ties are broken by `order_id` ascending, so the result is deterministic.

### `report.summary(ledger, now=0)`

Returns a dict with exactly these keys:
- `"count"`: number of orders
- `"open"`: number of open orders
- `"notional"`: total notional across all orders
- `"oldest_ts"`: the smallest `ts`, or `None` if there are no orders

### `report.group_by_status(ledger)`

Returns `{status: [order_id, ...]}` with order ids in **insertion order** within each
group, and groups in first-seen order.

### `report.expiring(ledger, now, window)`

Orders whose `status` starts with `"open"` and whose `age_seconds(now)` is **within**
`window` inclusive (`0 <= age <= window`). Results are ordered by `ts` ascending.

## Notes

- There is **at least one red herring**: code that looks wrong or slow but is correct.
  Do not change it.
- The failures are independent. Do not redesign the module to fix one.
- A zero-regression gate applies: breaking any currently passing test scores the
  whole task zero.
