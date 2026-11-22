# Fixture v4 — Rust repair (9.5/10)

Target difficulty: **9.5/10**. Domain: unsafe/raw pointers, `Arc<Mutex>`,
`Send`/`Sync` markers, `MaybeUninit` manual memory, zero-copy parsing,
performance contract and a scope trap.

## Layout

```
v4/
  task/
    AGENTS.md
    README.md
    src/lib.rs                16 behavioural bugs, no annotations
    tests/test_visible.rs     28 tests, ALL PASS on pristine
  _grader/
    pristine/                 copy of task/ used as the scoring baseline
    hidden_tests/test_hidden.rs  40 tests (16 FAIL / 24 PASS on pristine)
  README.md
```

## Bug inventory (16)

| # | Site | Wrong behaviour on pristine |
|---|------|-----------------------------|
| 1 | `RawVec::sum` | skips the last element |
| 2 | `RawVec::pop` | returns element 0 instead of the last |
| 3 | `RawVec::contains` | searches only the first half |
| 4 | `RawVec::reverse` | reverses only the first `len-1` elements |
| 5 | `SharedCounter::fetch_add` | returns the new value instead of the old |
| 6 | `SharedCounter::compare_set` | ignores `expected`, always writes, returns true |
| 7 | `SharedCounter::add_capped` | ignores `limit` |
| 8 | `Cell::replace_with` | returns the new value instead of the old |
| 9 | `Slot::init_count` | reports `init` (0/1) instead of total writes |
| 10 | `Slot::put_if_empty` | overwrites an initialized slot |
| 11 | `Slot::get_or` | always returns the default |
| 12 | `split_fields` | drops empty fields |
| 13 | `parse_pairs` | drops pairs with empty values |
| 14 | `first_field` | returns the whole string |
| 15 | `parse_int_field` | reads index `idx+1` |
| 16 | `prefix_sum` | does O(n²) work (n² counter increments) |

## Extra difficulty features

- **No annotations.** Unlike v3, the source has no `# BUG` markers.
- **No visible signal.** All 28 visible tests pass on pristine; the bugs are
  masked by inputs where buggy and correct outputs coincide.
- **Performance contract.** `test_h_perf_linear` resets `WORK`, calls
  `prefix_sum` with n = 1000 and requires `work() <= 2000`.
- **Scope trap.** `legacy_decode` is intentionally lenient (`"oops" -> 0`)
  and the `unsafe impl Send`/`Sync` on `RawVec` / `Cell` are intentional.
  Hidden tests require preserving all of them.
- **Zero-copy contract.** Hidden tests check that returned `&str` pointers lie
  inside the input buffer.

Every hidden test is satisfiable: the fixed reference passes all 40.

## Validation

See the validation report produced during construction. Scoring is performed
with `score_rust.py --fixture <v4> --solution <dir> --out <json>`:

- pristine solution: 28/28 visible PASS, 24/40 hidden PASS;
- fully fixed reference: 28/28 visible PASS, 40/40 hidden PASS, no regressions,
  `score_zero = false`.
