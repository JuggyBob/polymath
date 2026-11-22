# Gradebook repair task

Fix the bugs in `src/gradebook.cpp` so that every contract in `AGENTS.md` holds.

- Do not change `include/gradebook.h`.
- Do not change anything in `tests/`.

Build and run the visible tests:

```
cl /EHsc /nologo /Iinclude src\*.cpp tests\test_visible.cpp
test_visible.exe
```

Some visible tests fail on the starting code. That is expected feedback.
Hidden checks cover additional cases, so read all the contracts, not just the
visible failures.
