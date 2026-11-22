# Strata repair fixture v3 — Rust borrowing & dispatch

`src/lib.rs` is a small library that mixes borrowed views, shared counters,
a weak-linked tree, generic helpers and trait objects. Twelve implementation
bugs were planted. Each is marked with a `# BUG` comment in the source.

Run the visible suite:

```sh
rustc --edition 2021 -O tests/test_visible.rs -o visible.exe
visible.exe
```

Every line of output is `TEST <name> PASS|FAIL`. On the starting code 4 of the
16 visible tests pass; the other 12 expose planted bugs. Hidden tests probe the
same functions with different inputs and check deeper tree traversal,
clamped transfers and mixed trait-object lists.

The intended repair is to change only the buggy function bodies. Public names,
signatures and generic bounds must stay as they are. See `AGENTS.md` for the
full rules.
