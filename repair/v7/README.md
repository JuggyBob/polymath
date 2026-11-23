# Repair fixtures — v7 (hard cascading-fault edition)

Four language implementations of the same deliberately hard repair task:

| Folder | Language | Runner |
|---|---|---|
| `python/v7/` | Python 3, standard library only | `score_v7.py --lang python` |
| `cpp/v7/` | C++20 | `score_v7.py --lang cpp` |
| `js/v7/` | JavaScript / Node 22+ | `score_v7.py --lang js` |
| `rust/v7/` | Rust, standard library only | `score_v7.py --lang rust` |

All four are generated from the single canonical manifest
[`v7-tests.json`](v7-tests.json): 45 visible examples, 49 hidden tests and
three performance workloads. Test names and expected outputs are identical
across languages, so scores are comparable.

The shared contract is [`docs/V7-DESIGN.md`](../docs/V7-DESIGN.md). Measured
results, with caveats, are in [`docs/V7-RESULTS.md`](../docs/V7-RESULTS.md).

## What makes v7 harder

- **Masked faults.** Several bugs only become observable after a prerequisite
  bug is fixed. The task README tells the solver this is expected; each chain
  terminates and is discoverable from visible examples.
- **Cross-component inconsistencies.** Compiler/VM, lexer/parser, disassembler/
  serialiser and snapshot/checksum disagree with each other in plausible ways.
- **New features.** Deterministic fibers (`spawn`, `yield`, `join`) and a fully
  specified snapshot byte format with FNV-1a checksum and exact error codes.
- **Three performance gates** with per-language limits calibrated to at least
  3x the golden reference.

## Scoring

Same protocol as v1–v6: correctness and performance are reported separately.
Each perf test runs three times and reports all three times plus the median. A
performance failure never sets `score_zero`; only correctness regressions,
test tampering, public-API changes or compile failures do.

## Important limitations

The limitations in the parent [`README.md`](../README.md) apply here too. In
particular the fixtures are not a sandbox: a solver that can write outside its
own copy can interfere with grading. Always grade from an isolated run copy.
