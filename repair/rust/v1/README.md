# Rust repair v1 (5/10)

Ownership basics: Vec, Option, structs, borrowing, slices. Standard library only.
Nine public functions, seven planted behavioural bugs. The visible suite has
12 checks (several fail on the pristine code); the hidden suite has 18 checks
that cover empty slices, large integers, negative values, out-of-order
duplicates, boundaries and Unicode.

Give the model only `task/`, then score a repaired copy:

```
python <REPO>\repair\rust\score_rust.py --fixture <REPO>\repair\rust\v1 --solution <candidate-dir> --out <report.json>
```
