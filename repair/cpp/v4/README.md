# C++ repair v4-hard (9.5/10)

A numeric library with three parts: `Matrix` (row-major storage, arithmetic and
function-pointer reductions), `Algorithms` (pointer templates, sorted indices,
a 2000x2000 traversal with a 2-second contract) and `Registry` (named function
callbacks with a one-entry cache).

Adversarial fixture: all visible tests PASS on the pristine source, there are no
`# BUG:` markers, and the contracts are a mix of worked examples and prose.
Public headers and tests are frozen. Scoring uses MSVC `cl.exe` via `vcvars64.bat`.

Compile a trial by hand:

```
cl /EHsc /nologo /Od /Iinclude src\*.cpp tests\test_visible.cpp
```

Score a candidate (baseline, visible and hidden are built separately):

```
python <REPO>\repair\cpp\v4\_grader\score.py --fixture <REPO>\repair\cpp\v4 --solution <dir>
```

Files:

- `task/` — the candidate task (headers, sources, visible tests, AGENTS.md).
- `_grader/pristine/` — exact copy of `task/`, used for the zero-regression gate.
- `_grader/hidden_tests/test_hidden.cpp` - 41 checks named `test_h_*`.
- `_grader/score.py` — copy of the shared `score_cpp.py`; do not modify.
