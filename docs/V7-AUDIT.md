# v7 audit record

All work below was done by independent `opencode-go/hy4-flash-free` subagents.
First-round audits were read-only and were instructed to find genuine issues,
not style nits. Fixes were then applied by separate agents and re-audited from
scratch. Every fixture passed 8/8 post-fix checks.

## Round 1 findings

| Language | High / medium findings |
|---|---|
| Python | Hidden-only correctness regressions could never set `score_zero`, because the regression set intersected baseline *visible* names with hidden failures (disjoint namespaces). Demonstrated with a controlled 2-hidden-test break. 12 hidden tests had no visible-example basis. Permanently invisible faults in `OP_NAMES[SPAWN]`, `OP_NAMES[YIELD]` and the serialiser header. Generated `.pyc` files made the trees non-identical outside the scorer's ignore rules. |
| C++ | `h_array_alias` had no visible signal: a value-copy fault could pass all visible tests and fail only hidden. Agent-visible README documented `/Od` while the scorer built with `/O2`. Serialisation/disassembly APIs had no visible driver. |
| JavaScript | A source syntax error or failed `require` was classified as success: `compile.*=true`, 0 passed / 0 failed, `score_zero=false`. Three planted faults were invisible to the entire visible suite (structural `distinct`, `DUPLICATE_FIBER`, disassembly mnemonic). |
| Rust | Scorer omitted `public_api_intact`, `files_removed` and wall-clock timing. 13 hidden tests had no visible-example basis. No scorer copy under `_grader/`. |

Shared finding: absolute-millisecond perf limits are machine-specific; they
were kept but documented, and every limit is at least 3x the golden reference
measured here.

## Fixes applied

1. Canonical manifest expanded from 32 to 45 visible examples. The 13 additions
   cover array aliasing, nested `distinct`, Unicode comparison, serialisation
   round-trip, disassembly text, in-flight fiber snapshots, all five snapshot
   error codes and raw-bytecode execution.
2. Hidden-baseline regression detection added to every scorer: pristine is run
   against the hidden suite too, and `base_hidden_pass & hid_fail` is included
   in `regressions`. A hidden-only correctness regression now sets `score_zero`.
3. JavaScript compile-failure classification fixed: zero test lines, load
   errors, timeouts and build failures now set `score_zero`; a non-zero exit
   with real TEST lines remains a normal failing suite.
4. Rust scorer gained `public_api_intact`, `files_removed` and timing fields;
   all four scorers now write the same required field set and carry a
   byte-identical `_grader/` copy.
5. Permanently invisible faults were removed or exposed. In Rust, four
   behaviour-neutral hunks were corrected. In JavaScript, two zero-signal
   faults were restored to golden behaviour. In Python, the named faults and
   eleven other zero-signal faults were corrected.
6. Documentation fixed: example counts updated to 45; the C++ agent README now
   documents `/O2`; the C++ README points at the real scorer path.

## Round 2 (post-fix re-audits)

Each language was re-audited with fresh subagents against the updated manifest.
Checks covered: exact 45/45 visible and 49/49 hidden golden results; byte-exact
expected files in all three trees; complete scorer schema and identical scorer
copies; hidden-only regression probe; perf-only probe; file/API loss probe;
fault observability; pristine byte identity; and hygiene (no absolute paths,
credentials or grader references in agent-visible files).

All four returned **PASS 8/8**. One non-blocking note: the C++ hidden driver
sources contain extra coverage assertions beyond the manifest `source` strings;
names and expected outputs remain canonical, and the additions were required
to eliminate invisible faults.

A separate mechanical cross-language check confirmed identical example names,
expected bytes, hidden names and scorer copies across all four fixtures.
