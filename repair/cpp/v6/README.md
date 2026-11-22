# C++ repair v6 — spec-free MiniVM

A small stack virtual machine with a visible pipeline:
lexer → parser → compiler → bytecode → VM → disassembler → serialiser.

The agent workspace (`task/`) has no contract prose: the `task/examples/`
programs and the visible test harness are the only specification. Hidden
acceptance tests define the rest of correctness. Every hidden behaviour has a
visible example — including `distinct` — but some of those examples intentionally
fail on the starting source where a bug affects the whole input class. See
`task/README.md` for the list.

Scoring separates correctness from performance. A performance failure lowers the
performance score only; it never sets `score_zero`.

```
python <REPO>\repair\cpp\score_v6.py `
  --fixture <REPO>\repair\cpp\v6 `
  --solution <dir> `
  --out <report.json>
```

- `task/` — candidate workspace (README, headers, sources, examples, visible tests).
- `_golden/` — fully correct reference (never shown to the agent).
- `_grader/pristine/` — byte-identical copy of `task/`, for the zero-regression gate.
- `_grader/hidden_tests/test_hidden.cpp` — hidden acceptance and performance tests.
- `_grader/score_v6.py` — copy of the shared scorer.

Toolchain: MSVC `cl.exe` via `vcvars64.bat`, compiled with `/Od`.
