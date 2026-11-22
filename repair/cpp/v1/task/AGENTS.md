# Repair task C++ v1 — daily temperatures

A small C++ program that computes statistics over an array of daily temperatures.
**Some tests fail. Fix the code.**

## Rules

- Do not modify anything under `tests/`. Those files are frozen.
- Do not change `include/stats.h` (public API and struct layout).
- Standard C++ only. No third-party libraries.
- Keep fixes small and local.

## Build and run

```
cl /EHsc /nologo /Iinclude src\*.cpp tests\test_visible.cpp
test_visible.exe
```

## Contracts

- `max_temp(values, n)` / `min_temp(values, n)` — largest / smallest value.
- `average_temp(values, n)` — arithmetic mean as a `double`, with fractional part.
- `count_above(values, n, threshold)` — number of values **strictly greater** than
  `threshold`.
- `day_of_min(values, n)` — the **1-based** position of the first smallest value.
  With `{5, 2, 9}` the answer is 2; with `{2, 2, 9}` the answer is 1.
- `valid_range(value, lo, hi)` — true when `lo <= value <= hi`, both ends included.
- `swap_values(a, b)` — exchanges two integers by reference.
- `sum_even(values, n)` — sum of the **even** values.
- `sort_ascending(values, n)` — sorts `n` values in place, ascending. Must not read
  or write past the last element.
- `count_duplicates(values, n)` — number of **values that occur more than once**,
  counting each repeated value once. With `{3, 3, 3}` the answer is 1; with
  `{3, 3, 4, 4}` the answer is 2.

## Notes

- Some code may look suspicious. Keep every function correct; the hidden suite
  checks behaviour, not style.
- The visible tests are a subset of the checks. Read every contract above.
