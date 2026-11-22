# Rust repair v5-hard (10/10)

A single-source Rust crate covering const generics, zero-cost iterator helpers,
AoS/SoA cache layout, unsafe bit reinterpretation, enum niche layout, and an
exact-O(sqrt(n)) primality contract with a 1,000,000-candidate performance
budget. A second performance contract times a hot loop over `1 << 22` particle
records.

Adversarial fixture: all visible tests PASS on the pristine source, there are
no bug markers, and the contracts are a mix of worked examples and prose. A
frozen "legacy" helper is an explicit scope trap. Scoring uses
`rustc --edition 2021 -O` via the shared scorer.

Compile a trial by hand:

```
rustc --edition 2021 -O task/tests/test_visible.rs -o test_visible.exe
```

Score a candidate (baseline, visible and hidden are built separately):

```
python <REPO>\repair\rust\score_rust.py --fixture <REPO>\repair\rust\v5 --solution <dir>
```

Files:

- `task/` - the candidate task (source, visible tests, AGENTS.md, README.md).
- `_grader/pristine/` - exact copy of `task/`, used for the zero-regression gate.
- `_grader/hidden_tests/test_hidden.rs` - the hidden checks named `test_h_*`.
