# MiniVM v7 — design and build report

## What v7 is

v7 is a deliberately hard, spec-free, cross-cutting repair fixture in four
languages. It keeps v6's pipeline (lexer, parser, compiler, bytecode, VM,
disassembler, serialiser) and adds two features: deterministic fibers
(`spawn`, `yield`, `join`) and a fully specified snapshot byte format with a
checksum and five exact error codes.

The hard part is the fault structure. v6 design rule R5 forbade masked bugs.
v7 intentionally reverses it: several faults are only observable after their
prerequisite fault is fixed. Four to five terminating chains per language were
planted. The task README tells the solver that failures may be masked and that
new failures after a fix are expected, so this is difficult but not unfair.

## How it was built

1. A language-neutral contract was written first (`docs/V7-DESIGN.md`).
2. A single canonical manifest (`repair/v7-tests.json`) defines every example,
   hidden test and performance workload. All four languages use the same test
   names and expected bytes.
3. Four parallel `hy4-flash-free` subagents built one fixture each from the
   same contract. The golden implementations were verified before the broken
   task copies were derived from them.
4. Four independent audits found real defects, including a hidden-regression
   `score_zero` bug, a JavaScript syntax-failure classification bug, missing
   scorer report fields, derivability gaps and permanently invisible faults.
5. Four parallel fix agents corrected all of them. Four more independent
   post-fix audits passed 8/8 each.

## Difficulty compared with v6

| Dimension | v6 | v7 |
|---|---|---|
| Visible examples | ~12–40, depending on language | 45 canonical, identical across languages |
| Hidden tests | ~26–50 | 49 canonical |
| Perf gates | 2 | 3 |
| Masked fault chains | forbidden | 4–5 per language, terminating |
| Cross-component faults | at least 4 | 8–10 per language |
| New features | `DISTINCT` | fibers, snapshots, checksum, error codes |
| Fault count | ~25–30 | 41–45 per language |

Difficulty was increased without making hidden behaviour unknowable: after the
first audits, 13 canonical examples were added specifically so every hidden
behaviour has a visible anchor.

## Fairness controls

- Golden implementations pass 45/45 visible and 49/49 hidden in every language.
- Every planted fault is observable in the visible or hidden suite, either
  directly or after its prerequisite fix; chains terminate and have no cycles.
- Hidden tests that pass on the pristine source are baselined, so a
  hidden-only regression sets `score_zero` in all four scorers.
- A purely performance failure never sets `score_zero`.
- Compile/syntax/load failures set `score_zero`; a zero-test run is never
  treated as success.
- `task/` and `_grader/pristine/` are byte-identical in every language.
- No absolute paths, credentials or grader references appear inside any
  agent-visible `task/` directory.

## Known limits

- These are hand-written local fixtures, not official benchmark items.
- Anti-cheat is not sandboxed. A solver with access outside its own run copy
  could interfere with grading.
- Absolute millisecond perf limits are machine-specific. They were calibrated
  to at least three times the golden reference's measured time here.
- The C++ hidden driver sources contain extra coverage assertions beyond the
  manifest `source` strings. Names and expected outputs remain canonical; the
  additions were needed to eliminate permanently invisible faults.
- The model campaign did not complete in three of four languages; see
  `docs/V7-RESULTS.md`. No result was estimated or invented.
