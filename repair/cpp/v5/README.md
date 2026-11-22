# C++ repair v5-hard (10/10)

A small concurrent task scheduler with low-level C++: a 64-byte-aligned pool
with placement new, a lock-free single-producer/single-consumer ring buffer with
monotonic atomic cursors and cache-line padding, and a fixed-capacity task
scheduler with an O(sqrt(n)) prime-checking contract.

Adversarial fixture: all visible tests PASS on the pristine source, there are
no `# BUG:` markers, and the contracts are worked examples plus prose. Twenty
behavioural/performance defects are planted across the three translation units.
Public headers and tests are frozen. Scoring uses MSVC `cl.exe` via
`vcvars64.bat`.

Compile a trial by hand:

```
cl /EHsc /nologo /Od /Iinclude src\*.cpp tests\test_visible.cpp
```

Score a candidate (baseline, visible and hidden are built separately):

```
python <REPO>\repair\cpp\v5\_grader\score.py --fixture <REPO>\repair\cpp\v5 --solution <dir>
```

Files:

- `task/` — the candidate task (headers, sources, visible tests, AGENTS.md).
- `_grader/pristine/` — exact copy of `task/`, used for the zero-regression gate.
- `_grader/hidden_tests/test_hidden.cpp` — ~50 checks named `test_h_*`.
- `_grader/score.py` — copy of the shared `score_cpp.py`; do not modify.
