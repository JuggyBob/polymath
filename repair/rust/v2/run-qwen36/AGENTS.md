# Repair task Rust v2 — results, iterators and traits

A small Rust library that parses and aggregates labelled readings. It uses a
custom error enum, `FromStr`, `Display`, iterator adapters and `try_fold`.
**Some tests fail. Fix the code.**

## Rules

- Do not modify anything under `tests/`. Those files are frozen.
- Keep every public signature, the `ParseError` variants, the `Reading` fields
  and all trait implementations in `src/lib.rs` unchanged.
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

`ParseError` has five variants. `Display` must render them exactly as:

- `Empty` -> `empty input`
- `InvalidNumber(s)` -> `invalid number: {s}`
- `NegativeNotAllowed` -> `negative value not allowed`
- `OutOfRange` -> `value out of range`
- `UnknownUnit` -> `unknown unit`

`Reading { label: String, value: i64 }`. Its `Display` renders exactly
`"{label}: {value}"`, for example `cpu: 7`.

Parsing rules, used by both `parse_reading` and `FromStr for Reading`:
the input is trimmed; it must contain `=` with a non-empty label on the left;
the right side must parse as an `i64`. Failures map to `Empty` (empty input,
no `=`, empty label), `InvalidNumber(raw)` (the right side is not an integer),
`NegativeNotAllowed` (value < 0), or `OutOfRange` (value > 1000). Valid input
gives `Ok(Reading { label, value })`.

- `parse_reading(s) -> Result<Reading, ParseError>` — apply the parsing rules.
  It must **return** an error for bad input; it must never panic.
- `FromStr for Reading` — same rules, with one boundary: a trimmed-empty input
  must produce `Err(ParseError::Empty)`.
- `parse_all(lines) -> Result<Vec<Reading>, ParseError>` — parse every line in
  order. Return `Ok` with all readings only when every line is valid; return
  `Err` for the first invalid line. Never silently drop a line.
- `first_valid(lines) -> Option<Reading>` — the first line that parses
  successfully, in order, or `None` if none parse. Never panic on bad lines.
- `count_over(values, threshold) -> usize` — number of values **strictly
  greater** than `threshold`.
- `take_top_n(readings, n) -> Vec<i64>` — the `n` largest values, descending.
  Exactly `n` items when possible, fewer only when there are not enough values.
- `skip_first_n(readings, n) -> Vec<String>` — labels after skipping the first
  `n` readings, in original order. `n == 0` keeps all labels; `n` greater than
  the length gives an empty vector.
- `parse_scores(tokens) -> Vec<i64>` — the integers among `tokens`, in order;
  tokens that are not integers are omitted, not replaced.
- `sum_values(readings) -> Result<i64, ParseError>` — sum of the values, or
  `Err(NegativeNotAllowed)` if **any** value is negative. Empty input gives
  `Ok(0)`.
- `join_labels(readings) -> String` — labels joined by `", "` with no leading
  or trailing separator; empty input gives `""`.

## Notes

- The visible suite checks only part of the behaviour. Hidden checks cover
  empty collections, malformed input, negative values, boundaries, ordering
  and exact `Display` output. Read every contract above.
- Panics are caught per test and reported as `FAIL` for that test only.
