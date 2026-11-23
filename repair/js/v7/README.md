# MiniVM v7 — JavaScript repair fixture

Spec-free, cross-cutting repair benchmark. The agent sees only `task/`.
The examples in `task/examples/` (each a Node driver with `.expected` stdout)
are the visible specification; there is no separate contract document and no
`AGENTS.md`.

## Layout

- `task/` — agent workspace (broken implementation, 45 example drivers, visible
  test).
- `_golden/src/` — complete correct implementation; used only as a scoring
  target. Never copied into the agent workspace.
- `_golden/examples/` — the same 45 canonical drivers, run against golden.
- `_grader/pristine/` — byte-identical copy of `task/`.
- `_grader/hidden_tests/test_hidden.js` — 49 canonical hidden cases plus the
  three performance workloads.
- `score_v7.py` — scorer with separate `correctness` and `performance` blocks.

## Language surface

The implementation is CommonJS, Node 18+. `src/index.js` is the public entry
point: `MiniVM`, `MiniVMError`, `run`, `compileSource`, `execute`, `serialize`,
`deserialize`, `disassemble`, `restore`, `snapshot`, `OP`, `OP_NAMES` and
`runtime`. Snapshots are Buffers; `restore` throws `MiniVMError` whose message
is one of `BAD_MAGIC`, `BAD_VERSION`, `TRUNCATED`, `BAD_CHECKSUM`,
`DUPLICATE_FIBER`.

## Scoring

```
python score_v7.py --fixture <this dir> --solution <dir to score> --lang js --out <json>
```

Correctness comes from `TEST` lines; performance from `PERF` lines (three runs
per perf test, with the median reported). Limits: `perf_print` 250 ms,
`perf_disasm` 200 ms, `perf_snapshot` 250 ms. A performance failure never sets
`score_zero`; only correctness problems, test tampering or missing files do.

On the pristine source, 31 of the 45 visible examples fail. The golden passes
all 49 hidden cases and all three perf gates; measured medians are recorded in
`verification.txt`.

## Caveats

- Failures in `task/` may be masked by prerequisite faults. That is deliberate:
  the task README warns the solver, and each chain terminates.
- Boolean negation is ordinary logical negation. Equality is strict: cross-type
  comparisons (`1 == true`, `null == false`) are false with no numeric coercion.
- No process kills, config changes or git changes are used during validation.
