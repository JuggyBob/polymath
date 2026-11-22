# Repair task C++ v3 — StringMap and Buffer

A string-keyed hash map built with raw pointers and open addressing, plus a
small class that owns a dynamic array. Some tests fail on the starting code.

Read `AGENTS.md` first. It lists every contract, the build command and worked
hash examples.

## Build and run

```
cl /EHsc /nologo /Od /Iinclude src\*.cpp tests\test_visible.cpp
test_visible.exe
```

## Files

- `include/map.h` — public API. Do not change it.
- `src/map.cpp` — all of the implementation. Fix the bugs here.
- `tests/test_visible.cpp` — frozen visible checks.
- `AGENTS.md` — contracts and rules.

## Score from the fixture root

```
python <REPO>\repair\cpp\v3\_grader\score.py --fixture <REPO>\repair\cpp\v3 --solution <directory>
```
