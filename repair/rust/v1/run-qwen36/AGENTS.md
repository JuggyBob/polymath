# Repair task Rust v1 — ownership basics

A small Rust library of functions over slices, `Option`, structs of data and strings.
**Some tests fail. Fix the code.**

## Rules

- Do not modify anything under `tests/`. Those files are frozen.
- Keep every public function signature in `src/lib.rs` unchanged.
- Standard library only. No third-party crates and no `Cargo.toml` are needed.
- Keep fixes small and local. Fix the behaviour, not the tests or the contracts.

## Build and run

```
rustc --edition 2021 -O tests/test_visible.rs -o test_visible.exe
test_visible.exe
```

Each test prints `TEST <name> PASS` or `TEST <name> FAIL`. A panic in one test is
caught and reported as `FAIL` for that test only; it does not hide the other results.

## Contracts

- `sum(values: &[i32]) -> i64` — the mathematical sum of all values, returned as
  `i64`. An empty slice gives `0`. The answer must stay correct when the `i32`
  values are large: widen before adding, do not let `i32` arithmetic wrap.
- `max(values: &[i64]) -> Option<i64>` — the largest value, or `None` for an
  empty slice. Must never panic, including on empty input.
- `average(values: &[i64]) -> Option<f64>` — the arithmetic mean as an `f64`
  with its fractional part intact (`[1, 2, 3, 4]` gives `2.5`), or `None` for an
  empty slice.
- `count_matching(values: &[i64], target: i64) -> usize` — the number of values
  **exactly equal** to `target`. Values greater than `target` do not count.
- `unique_sorted(values: &[i64]) -> Vec<i64>` — a sorted (ascending),
  duplicate-free copy. Duplicates must be removed even when they are not
  adjacent in the input. An empty slice gives an empty vector.
- `chunk(values: &[i64], size: usize) -> Vec<Vec<i64>>` — consecutive chunks of
  exactly `size` elements, with the last chunk possibly shorter. `size == 0`
  gives an empty vector. Chunks must preserve input order.
- `clamp(value: i64, lo: i64, hi: i64) -> i64` — `lo` when `value < lo`, `hi`
  when `value > hi`, otherwise `value`. Assume `lo <= hi`.
- `word_count(s: &str) -> usize` — number of words separated by Unicode
  whitespace (spaces, tabs, newlines, etc.). Empty or whitespace-only input
  gives `0`.
- `char_count(s: &str) -> usize` — number of Unicode characters (scalar
  values), **not** the number of UTF-8 bytes. `"héllo"` has 5 characters.

## Notes

- The visible suite checks only part of the behaviour. Hidden checks cover
  empty slices, large integers, negative values, out-of-order duplicates,
  boundaries and Unicode. Read every contract above rather than only chasing
  the visible failures.
