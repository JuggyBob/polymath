# C++ repair v2 (6.5/10) — gradebook

A small gradebook built on `std::vector<Record>` and `std::string`. Ten public
functions, nine planted defects. The public header is fixed; repair the
implementation in `task/src/gradebook.cpp`. Visible tests give feedback; hidden
tests check additional cases.

Layout:

- `task/` — the candidate task (`include/`, `src/`, `tests/`, `AGENTS.md`, `README.md`)
- `_grader/pristine/` — untouched copy of `task/`, used for the zero-regression gate
- `_grader/hidden_tests/test_hidden.cpp` — hidden checks
- `_grader/score.py` — copy of the shared C++ scorer (do not modify)

Build the visible tests from `task/`:

```
cl /EHsc /nologo /Iinclude src\*.cpp tests\test_visible.cpp
test_visible.exe
```

Score a solution:

```
python <REPO>\repair\cpp\score_cpp.py --fixture <REPO>\repair\cpp\v2 --solution <dir>
```
