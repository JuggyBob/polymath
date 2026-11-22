# C++ repair v5-hard — task

Fix the behaviour described in `AGENTS.md`. Edit only `src/*.cpp`.

```
cl /EHsc /nologo /Od /Iinclude src\*.cpp tests\test_visible.cpp
test_visible.exe
```

`include/` and `tests/` are frozen. The visible tests all pass on the starting
source; they are not a full specification. Read the worked contracts in
`AGENTS.md` rather than inferring rules from what the visible tests check.
