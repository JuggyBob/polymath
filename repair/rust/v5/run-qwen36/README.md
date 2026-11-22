# Rust repair v5 - task

Fix the behaviour described in `AGENTS.md`. Edit only `src/lib.rs`.

```
rustc --edition 2021 -O tests/test_visible.rs -o test_visible.exe
test_visible.exe
```

`AGENTS.md`, this file, and `tests/` are frozen. The visible tests all pass on
the starting source; they are not a full specification.
