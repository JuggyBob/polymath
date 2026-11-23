# MiniVM v7 — shared design spec

Purpose: a deliberately hard, spec-free, cross-cutting, long-horizon repair
benchmark in four languages. Four implementations, one conceptual shape, one
canonical set of example programs and hidden tests. Read this before building.

**This version intentionally breaks a v6 rule.** v6 design rule R5 said "do NOT
create a bug that is deliberately masked by a second bug". v7 requires the
opposite: several bugs are *masked* and only become observable after their
prerequisite fault is fixed. This is the primary difficulty increase. Fairness
is preserved by telling the solver, in the task README, that failures may be
masked and that new failures after a fix are expected.

## Non-negotiables

1. **No `AGENTS.md`.** The agent workspace contains only `README.md`, source
   files and `examples/`.
2. **Examples are the spec.** The canonical `examples/` manifest in
   `repair/v7-tests.json` is copied byte-for-byte into every language. Most
   examples pass on the pristine source; a documented minority fail. Together
   they are sufficient to infer every behaviour the hidden tests check,
   *after* the masking faults are removed.
3. **Golden reference.** A fully correct implementation lives in `_golden/src/`,
   outside the agent workspace. It must pass 100% of hidden tests and all perf
   gates. Never expose it to the model.
4. **Performance scored separately.** The scorer emits `correctness` and
   `performance` blocks. Each perf test runs exactly three times; report all
   three and the median. Limits are per-language constants at least 3x the
   golden reference's measured time on the reference machine. A perf failure
   reduces the performance score but MUST NOT set `score_zero`.
5. **Masked faults are allowed, but must be discoverable.** For every masked
   bug, the prerequisite bug must itself be discoverable from visible examples.
   The chain terminates; there are no cycles and no permanently invisible bug.
6. **Language-neutral features.** Fibers, snapshots and the mini-language are
   defined here, not in host-language idioms. No `asyncio`, `std::thread`,
   promises, channels, `pickle` or `serde_json`.

## Architecture (unchanged pipeline, plus two layers)

```
lexer → parser → compiler → bytecode → VM → disassembler → serialiser
                                        ↘ scheduler → snapshot
```

Suggested surface (adapt names to the host language, keep semantics identical):
- values: integers (signed 64-bit), strings (Unicode), booleans, null, arrays
- ops: push literal, + - * /, < > <= >= == !=, unary -, logical `!`, concat,
  `len`, jump / conditional jump, dup / pop / swap, load / store, print, halt,
  array new / push / get, `distinct`
- `run(source) -> stdout` convenience function
- disassembler that renders bytecode as readable text
- serialiser that writes bytecode to a compact text form and reads it back
- `snapshot` / `restore` of full VM state (see below)

## New cross-cutting features

### A. Deterministic fibers

Mini-language syntax (identical in all four languages):

```
fiber worker { print 1; yield; print 2; }
let f = spawn worker;
join f;
print 3;
```

- `fiber NAME { ... }` declares a fiber body, compiled as a code block ending
  in `HALT`. Declarations execute nothing.
- `spawn NAME` pushes a new fiber id (integer, starting at 1) onto the current
  fiber's stack and appends the fiber to the ready queue. It does not switch.
- `yield` suspends the current fiber, moves it to the ready-queue tail, and
  transfers control to the next ready fiber.
- `join <expr>` pops a fiber id. If that fiber has halted, continue. Otherwise
  block the current fiber on it and switch. When the target halts, blocked
  fibers are moved to the ready tail in the order they blocked.
- Scheduler: FIFO ready queue, run-to-yield/halt/block quanta. Print output is
  therefore fully deterministic and part of the hidden-test contract.
- Fibers share the global variable table but own their operand stacks and
  program counters. Snapshots include ready queue, blocked map and all fibers.

### B. Snapshot / restore

Host-level API (called by hidden tests, not from the mini-language):

- `snapshot(vm) -> bytes` and `restore(bytes) -> vm`.
- Binary layout, exactly:
  - magic bytes `M`, `V`, `7`, version byte `1`
  - u32 little-endian opcode count, then each opcode as tag byte + operands
  - u32 little-endian global count, then each name/value pair (u32 len + UTF-8
    bytes for the name; 1 type byte + payload for the value; strings use u32
    byte length; integers use 8-byte little-endian two's complement)
  - u32 little-endian fiber count, then each fiber's id, pc, stack depth and
    stack values in the same value encoding
  - ready-queue fiber ids as u32 count + u32 ids
  - blocked pairs as u32 count + (waiter id, target id) u32 pairs
  - final 4-byte FNV-1a 32-bit checksum over every preceding byte
- Errors are exact strings surfaced by the API: `BAD_MAGIC`, `BAD_VERSION`,
  `TRUNCATED`, `BAD_CHECKSUM`, `DUPLICATE_FIBER`.
- Restore must be a pure function of the byte buffer: no host state leaks in.

## Masked fault catalogue (implement in `task/`, fix in `_golden/`)

Plant 38–45 natural bugs across 9–11 files. At least:
- 8 cross-component inconsistencies (compiler opcode vs VM dispatch, lexer
  token vs parser node, disassembler token vs serialiser name, etc.)
- 10 masked faults forming at least 4 distinct chains, for example:
  1. lexer emits `GREATER` for `>=`; after fixing that, parser still lacks the
     `>=` node; after fixing that, compiler maps it to the compare opcode with
     swapped operands.
  2. VM lacks the fiber scheduler case; after adding it, `yield` does not rotate
     the ready queue; after fixing that, `join` on a halted fiber deadlocks.
  3. serialiser omits new opcodes; after adding them, negative integers are encoded
     as unsigned; after fixing that, the checksum covers the wrong byte range.
  4. array `push` stores a value copy; after fixing to store a reference, nested
     arrays alias incorrectly; after fixing that, `distinct` uses identity rather
     than structural equality.
- 6 sequence-dependent bugs (only appear after a sequence of operations, e.g.
  snapshot → mutate → restore → run).
- 4 performance defects with correctness preserved: O(n^2) string accumulation
  in the print loop, O(n^2) disassembly, O(n^2) snapshot buffer copying, linear
  variable lookup that should be indexed.
- No comments, TODOs or markers identifying any bug.

## Canonical tests

`repair/v7-tests.json` is the single source of truth. It contains:
- `examples`: name, source, expected stdout. Copied into every `task/examples/`.
- `hidden`: name, source, expected stdout, and kind (`run`, `exec`, `serial`,
  `snapshot`). Copied into every `_grader/hidden_tests/`.
- `perf`: name, workload, per-language median limits in ms.

Do not invent extra hidden tests that are not in the manifest. Do not change
expected outputs. Every language must report the same test names.

## Fixture layout

```
v7/
  README.md                 layout, scoring, caveats
  task/
    README.md               task statement (shared wording, see below)
    src/...                 broken implementation (agent workspace)
    examples/               canonical examples
  _golden/
    src/...                 correct implementation
    examples/               canonical examples
  _grader/
    pristine/               byte-identical copy of task/
    hidden_tests/...        canonical hidden tests only
    score_v7.<ext>          scorer with correctness/performance blocks
  run-<label>/              created by the runner, never committed
  <label>-score.json        written by the scorer
```

## Test output protocol

Correctness tests print one line each:

```
TEST <name> PASS
TEST <name> FAIL
```

Performance tests print one line per run (exactly 3 runs per test):

```
PERF <name> <milliseconds> PASS
PERF <name> <milliseconds> FAIL
```

The scorer reports `correctness` (passed/failed from TEST lines) and
`performance` (passed/failed from PERF lines, with all three times and the
median). A PERF FAIL never sets `score_zero`; only correctness problems do.
Scorers must also write `regressions`, `tests_modified`, `tests_added`,
`tests_removed`, `files_removed`, `public_api_intact`, and wall-clock timing.

## Task README (shared wording, adapt only the run command)

The workspace README must state, and no more:

- "This VM is broken in several ways. Hidden acceptance tests define
  correctness. Run the examples to see the intended behaviour."
- "Failures may be masked by earlier faults. After a fix, re-run everything:
  new failures are expected and are part of the task."
- "Do not change the example files. The visible tests and examples are the
  only specification."
- How to compile/run one example and the visible suite for that language.

Do not disclose the bug catalogue, the feature names beyond what the examples
show, the grader path, or the canonical hidden-test list.

## Validation standard

- The golden must reach 100% correctness and pass every perf gate in its own
  language. Record the raw times.
- The pristine source must produce at least one visible FAIL (documented count
  in the manifest) and must NOT pass the hidden suite.
- Independent subagents audit each hidden test for derivability from examples,
  each masked chain for termination, and each scorer for the PERF/score_zero
  rules. Any failure is fixed before publication.
- No process kills; no config, model, engine or git changes during validation.
