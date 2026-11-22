# Rust repair v2 — results, iterators and traits

`Result` and custom error enums, `FromStr`, `Display`, iterator adapters,
`fold`/`try_fold`. Nine behavioural bugs are planted in `src/lib.rs`. The
visible tests fail, so you get feedback; the hidden suite checks the full
contracts.

Edit `src/lib.rs` only. Then build and run the visible test:

```
rustc --edition 2021 -O tests/test_visible.rs -o test_visible.exe
test_visible.exe
```

See `AGENTS.md` for the exact contracts and rules.
