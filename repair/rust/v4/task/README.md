# Strata repair fixture v4 — unsafe Rust & shared state

`src/lib.rs` combines a raw-pointer owned buffer, `Arc<Mutex<_>>` state,
explicit `Send`/`Sync` markers, `MaybeUninit`-based manual initialization and
borrowed zero-copy parsing. Sixteen implementation bugs were planted. They are
**not** annotated in the source.

```sh
rustc --edition 2021 -O tests/test_visible.rs -o visible.exe
visible.exe
```

All 28 visible tests pass on the starting code. They exercise the API with
inputs chosen so the planted bugs stay hidden; they are a smoke test, not the
contract. Hidden tests (`test_h_*`) probe every documented behaviour, including
a linear-work performance contract for `prefix_sum` and the zero-copy pointer
guarantee for the parsers.

Repair only `src/lib.rs`; leave the tests and the public API unchanged. Some
code that looks suspicious is intentional — see `AGENTS.md` for the scope
boundary.
