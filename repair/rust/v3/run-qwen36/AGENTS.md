# Repair task (v3)

The library in `src/lib.rs` has **12 planted behavioural bugs**. The public API is
already correct in shape: do not rename functions, types, or fields, and do not
change signatures. Fix the bodies so every function matches its doc comment.

## Rules

- Edit **only** `src/lib.rs`. Do **not** modify `tests/test_visible.rs`, add or
  remove test files, or touch anything outside `task/`.
- The code must compile with `rustc --edition 2021 -O`.
- Some visible tests already fail. Those failures are real bugs; fix them.
- Hidden tests cover the same API more thoroughly. A correct fix should make
  both visible and hidden tests pass.
- Keep the existing public signatures, including generic bounds. Several
  bounds look stricter than needed but are part of the API contract.

## How to check locally

```sh
rustc --edition 2021 -O tests/test_visible.rs -o visible.exe
visible.exe
```

Each test prints `TEST <name> PASS` or `TEST <name> FAIL`. Aim for all PASS.

## Domain notes

This fixture focuses on:

- values borrowed from inputs and lifetime elision,
- `Rc<RefCell<_>>` interior mutability and lost-update patterns,
- `Weak` parent links and shared-tree traversal,
- generic helpers and cache lookups,
- dynamic dispatch through `dyn Shape`.

Watch for "fixes" that compile by cloning or by changing a borrow but silently
change behaviour (for example dropping a write-back). Correctness is judged by
the values returned and stored, not by whether the borrow checker is satisfied.
