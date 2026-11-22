# Repair task: telemetry event log

A small in-memory event log used by a reporting CLI. **All visible tests pass.
The implementation is still wrong. Fix it.**

## Rules

- Do not modify anything under `tests/`. Those files are frozen.
- Do not remove or rename public functions, classes or arguments.
- Standard library only. No dependencies. Keep fixes small and local.
- Do not change the `Event` field names.

## Verifying

```
python -m unittest discover -s tests -v
```

Green visible tests are **not** evidence of correctness. Every hidden test checks
a contract the visible suite never exercises. Read this file against the code.

## Event (`telemetry/events.py`)

- `Event(event_id, ts, kind, value, tags=None)`. `tags` is a **mutable list** of
  strings, empty by default. Two events with the same `event_id` are equal.
- Two events with the same `event_id` are the same event. Events are used as
  dictionary keys and in sets. What makes two events equal must stay consistent
  with what makes them hashable, even after a tag is appended.

## EventLog (`telemetry/log.py`)

- `append(event)` adds to the event list and the id index; duplicate id raises `ValueError`.
- `get(event_id)` returns the event or raises `KeyError`.
- `all_events()` returns a new list. Mutating it must not affect the log.

- `window(start, end)` selects events by timestamp. Worked examples:
  - events at ts 10, 20, 30 → `window(10, 30)` gives ts 10 and 20, **not** 30
  - events at ts 10, 20, 30 → `window(0, 25)` gives 10 and 20
  - events A(ts 10), B(ts 10) inserted in that order → `window(0, 20)` gives **B then A**
  - result is ordered by timestamp, with the ordering above applied to ties.

- `by_kind(kind)` returns events of that kind in insertion order.
- `prune(before)` drops every event with `ts < before` from **both** the list and
  the id index, and returns those ids sorted. It must not skip interleaved events.
- `latest(n=1)` returns the `n` most recent events. Worked examples:
  - A(ts 1), B(ts 5), C(ts 3) → `latest(2)` gives B, C
  - A(ts 5), B(ts 5) → `latest(2)` gives B, A
  - `n < 0` raises `ValueError`; `n == 0` gives `[]`.
  - Any mutation of the log invalidates a previously computed result.
  - The result must not depend on Python's hash seed.

- `total()` is the exact integer sum of values.
- `snapshot()` returns an independent copy of the id→event mapping. Appending a
  tag to an event obtained from a snapshot must not change the log's event.
- `clear()` resets the list, the index and any cached result.

## Reporting (`telemetry/metrics.py`)

Every function here is read-only. Calling one must not change what any log method
returns afterwards.

- `load(log)` — number of events.
- `rate(log, start, end)` — `len(window(start, end)) / (end - start)` as a float;
  `end <= start` raises `ValueError`.
- `rolling_sum(log, start, end)` — sum of values of events in the same window
  that `window(start, end)` would return. A caller relies on this agreement.
- `top_kinds(log, n=3)` — `(kind, total_value)` pairs for the largest totals.
  Worked examples:
  - cpu=300, mem=200 → `[("cpu", 300), ("mem", 200)]`
  - zeta=5, alpha=5 → `[("alpha", 5), ("zeta", 5)]`
  - `n < 0` raises `ValueError`. Output must not depend on the hash seed.
- `slow_rank(log)` — events by value descending; for equal values, smaller
  `event_id` first. Worked example: A(value 10), B(value 10) → A, B.
  It must return within two seconds for 10,000 events.

## Iteration helpers (`telemetry/itertools_helpers.py`)

- `iter_kinds(log)` is a generator yielding each distinct kind once, in first-seen
  order. Calling it twice on the same log must yield the same sequence.
- `traced(fn)` is a decorator that calls `fn` and returns its result. It must
  preserve the wrapped function's `__name__` and `__doc__`.
- `make_filter(kind)` returns a function taking an event and returning whether
  its kind matches. Each returned function must capture its **own** kind.

## Context (`telemetry/context.py`)

- `paused(log)` is a context manager. Inside the block, `append` must be a no-op.
  On exit — including exit by exception — the log's append behaviour must be
  exactly what it was before the block.

## Caching (`telemetry/cache.py`)

- `ResultCache.get(key, producer)` returns the cached value for `key`, calling
  `producer()` on a miss. The cache key must distinguish different requests:
  `get("x", lambda: 1)` then `get("y", lambda: 2)` must return 1 and 2.
  `clear()` empties it.

## Formatting (`telemetry/format.py`)

- `format_summary(log)` returns `"<count> events, total <value>"`.
  It is correct. You may simplify it if you think that helps, but its behaviour
  is checked.

## Notes

- Some code is correct but looks suspicious. Do not change correct code.
- The order in which reporting functions and log queries are called matters in
  several hidden tests.
- A zero-regression gate applies: breaking any currently passing test scores zero.
