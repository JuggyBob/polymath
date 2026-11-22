# Rust repair v2 (6.5/10)

`Result` and custom error handling, iterators and trait impls. Standard library
only. Nine planted behavioural bugs. The visible suite has 14 checks (most fail
on the pristine code); the hidden suite has 20 checks covering empty
collections, malformed input, negative values, boundaries, ordering and exact
`Display` output.

Give the model only `task/`, then score a repaired copy:

```
python <REPO>\repair\rust\score_rust.py --fixture <REPO>\repair\rust\v2 --solution <candidate-dir> --out <report.json>
```
