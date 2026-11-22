# Fixture v3 — Rust repair (8/10)

Target difficulty: **8/10**. Domain: lifetimes, `Rc`/`RefCell` interior
mutability, generics and trait objects.

## Layout

```
v3/
  task/                       given to the repair agent
    AGENTS.md
    README.md
    src/lib.rs                12 annotated behavioural bugs
    tests/test_visible.rs     16 tests (12 FAIL on pristine, 4 PASS)
  _grader/
    pristine/                 copy of task/ used as the scoring baseline
    hidden_tests/test_hidden.rs  24 tests (12 FAIL / 12 PASS on pristine)
  README.md                   this file
```

## Bug inventory (12)

| # | Site | Wrong behaviour on pristine |
|---|------|-----------------------------|
| 1 | `longer` | ties resolve to `b` |
| 2 | `first_word` | returns the whole string |
| 3 | `choose` | prefers non-empty `b` over `a` |
| 4 | `Slice::sum` | drops the final element |
| 5 | `Counter::with` | computes but never stores `f(v)` |
| 6 | `Counter::transfer` | credits `n` instead of clamped amount |
| 7 | `Node::parent_name` | returns own name instead of parent's |
| 8 | `Node::descendant_count` | counts only direct children |
| 9 | `max_by_key` | uses `min_by_key` |
| 10 | `Cache::get_or` | always returns the default |
| 11 | `Rect::area` | `w + h` instead of `w * h` |
| 12 | `describe` | hard-codes `"rect"` for every shape |

Traps represented: a borrow-checker-friendly clone with no write-back (5),
a stale-snapshot update (6), a `Weak` link that is never upgraded (7), an
unnecessary-but-required `Clone` bound (9), and dynamic dispatch replaced by a
constant (12).

## Validation

See the validation report produced during construction. Scoring is performed
with `score_rust.py --fixture <v3> --solution <dir> --out <json>`:

- pristine solution: 4/16 visible PASS, 12/24 hidden PASS;
- fully fixed reference: 16/16 visible PASS, 24/24 hidden PASS, no regressions,
  `score_zero = false`.
