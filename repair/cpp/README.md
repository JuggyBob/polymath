# C++ repair track

Six agentic repair fixtures in C++, ordered by difficulty. Separate from the Python
`repair\` track because C++ adds compilation, headers, pointer ownership and a
stricter class of mistakes.

| Fixture | Target | Domain | Visible failures on pristine |
|---|---|---|---|
| `v1/` | 5/10 | Temperature statistics: arrays, loops, functions, references | yes — feedback available |
| `v2/` | 6.5/10 | Gradebook with `vector`/`string`, records, state across calls | yes |
| `v3/` | 8/10 | String hash table with raw pointers, open addressing, rule of three | yes |
| `v5/` | 10/10 | Async ring queue, allocator, scheduler; contract-only | no - contract-only |
| `v6/` | 10/10 | Spec-free MiniVM: lexer/parser/compiler/VM/disassembly/serialisation | no - examples-based |
| `v4/` | 9.5/10 | Matrices, function pointers, templates, performance contracts | **no** — contract-only |

## Layout of each fixture

```
vN/
  task/                    agent workspace
    AGENTS.md              contracts and rules
    include/               public headers (do not change)
    src/                   implementation with planted bugs
    tests/test_visible.cpp visible assertion harness
  _grader/
    pristine/              clean baseline copy
    hidden_tests/          hidden assertion harness (outside the workspace)
    score.py               compile-and-score harness
```

## Scoring

```powershell
python <REPO>\repair\cpp\score_cpp.py `
  --fixture <REPO>\repair\cpp\v1 `
  --solution <candidate-dir> `
  --out <report.json>
```

The scorer compiles with MSVC `cl.exe` (via `vcvars64.bat`), runs the visible and
hidden test binaries separately, parses `TEST <name> PASS|FAIL` lines, checks that
tests and headers were not modified, and applies a zero-regression gate against
the pristine baseline. Compile errors are hard failures.

## Toolchain

- MSVC `cl.exe` 14.44 at
  `<PROGRAM_FILES> (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\Hostx64\x64`
- Environment set through
  `<PROGRAM_FILES> (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat`
- Do not assume a POSIX toolchain; the scorer uses MSVC `cl.exe`.

## Calibration note

The v1/v2 targets were chosen against the user's actual school work in
`<SCHOOL>\Informatica\Laboratorio\CPP`: iostream, prototypes, loops, switch, C
arrays with size parameters, const, references, structs. Raw pointers, hash
tables, templates and manual memory management do not appear there, so v3/v4
are deliberately new territory.

All fixtures are hand-written local tests, not official benchmarks.
