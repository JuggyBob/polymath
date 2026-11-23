# C++ repair v7 — spec-free MiniVM with masked faults

A mini-language VM: lexer → parser → compiler → bytecode → VM → disassembler →
serialiser, plus deterministic fibers and binary snapshot/restore.

The agent workspace (`task/`) has no contract prose. The 45 programs and drivers
in `task/examples/` and the visible harness are the only specification. Hidden
acceptance tests define the rest of correctness. Some failures on the starting
source are **masked**: a later fault only becomes observable after an earlier
one is fixed. The task README says so explicitly; this is intentional.

On the starting source, 32 of the 45 visible examples fail and 13 pass. The
golden implementation passes all visible and hidden tests.

Scoring separates correctness from performance. Each performance workload runs
exactly three times and reports all three times and the median. C++ limits are
60 ms (`perf_print`), 50 ms (`perf_disasm`) and 60 ms (`perf_snapshot`). A
performance failure lowers the performance block only; it never sets
`score_zero`.

```
python <REPO>\repair\cpp\v7\score_v7.py `
  --fixture <REPO>\repair\cpp\v7 `
  --solution <dir> `
  --out <report.json>
```

- `task/` — candidate workspace (README, headers, sources, examples, visible tests).
- `_golden/` — fully correct reference (never shown to the agent).
- `_golden/examples/` — the same 45 canonical examples.
- `_grader/pristine/` — byte-identical copy of `task/`, for the zero-regression gate.
- `_grader/hidden_tests/test_hidden.cpp` — the 49 canonical hidden tests and 3 performance workloads.
- `_grader/score_v7.py` — copy of the shared scorer.

Toolchain: g++ with `-std=c++17`, or MSVC `cl.exe` via `vcvars64.bat` with `/O2`
(the scorer uses MSVC with `/O2`). No absolute paths or secrets appear in this fixture;
`<REPO>` stands for the repository checkout.
