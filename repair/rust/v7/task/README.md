# MiniVM

This VM is broken in several ways. Hidden acceptance tests define correctness.
Run the examples to see the intended behaviour.

Failures may be masked by earlier faults. After a fix, re-run everything:
new failures are expected and are part of the task.

Do not change the example files. The visible tests and examples are the
only specification.

## Running an example

From this directory, with rustc 1.100 on the PATH:

```
rustc --edition 2021 -O examples/prog01_arith.rs -o prog01
./prog01
```

Compare the output with `examples/prog01_arith.expected`.

## Running the visible suite

```
rustc --edition 2021 -O tests/test_visible.rs -o test_visible
./test_visible
```
