# MiniVM v7 — Python fixture

Spec-free, cross-cutting repair fixture, Python 3 standard library only. The
agent workspace is `task/`; the correct reference is `_golden/`; grading
material is in `_grader/`.

```
v7/
  README.md                 this file
  task/
    README.md               task statement
    src/vm/                 broken implementation (agent workspace)
    examples/               45 driver .py files + .expected files
    tests/test_visible.py   visible suite
  _golden/
    src/vm/                 correct implementation
    examples/               same 45 drivers + expected files
  _grader/
    pristine/               byte-identical copy of task/
    hidden_tests/           canonical hidden suite only
  score_v7.py               scorer
  verification.txt          measured verification results
```

## Grading

```
python score_v7.py --fixture <REPO>/repair/python/v7 --solution <REPO>/repair/python/v7/task --lang python --out <out>/v7-score.json
```

The scorer emits separate `correctness` and `performance` blocks. Correctness
counts `TEST <name> PASS|FAIL` lines for the visible and hidden suites. Each
performance workload runs exactly three times and reports all three times plus
the median. A performance FAIL lowers the performance block only; it never sets
`score_zero`. Only correctness regressions, test tampering, removed source
files, public-API drift or compile failures do. The scorer baselines the
pristine source on both suites, so a hidden test that passes on pristine and
fails on a solution is a correctness regression. The scorer also reports
`regressions`, `tests_modified`, `tests_added`, `tests_removed`,
`files_removed`, `public_api_intact` and wall-clock timing.

Python limits are 900 ms for `perf_print`, 700 ms for `perf_disasm` and 700 ms
for `perf_snapshot`.

## Measured state

The golden reaches 49/49 hidden passes and passes all three performance gates.
The visible suite emits exactly 45 checks, one per canonical example. The
pristine source fails 28 of those 45 checks (17 pass), so at least one visible
FAIL is guaranteed. Masked faults are intentional: fixing one fault can expose
another that was hidden behind it.

## Caveats

The canonical manifest is `../../v7-tests.json`; the shared contract is
`../../../docs/V7-DESIGN.md`. Examples are the specification and must not be
changed in a solution. Hidden tests are injected only at grading time and are
never part of the agent workspace. This fixture is not a sandbox: grade from an
isolated run copy. Paths in this fixture are relative or placeholders.
