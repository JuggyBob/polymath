# MiniVM

This VM is broken in several ways. Hidden acceptance tests define correctness.
Run the examples to see the intended behaviour. Do not change the example files.

## Running an example

From this directory, with rustc 1.100 on the PATH:

```
rustc --edition 2021 -O examples/prog01_arith.rs -o /tmp/prog01
/tmp/prog01
```

Compare the output with `examples/prog01.expected`. Every example except the
DISTINCT ones passes on the code as it stands; they show the behaviours that
matter.

The `prog13_distinct_*`, `prog14_distinct_*`, `prog15_distinct_*` and
`prog16_distinct_*` examples are the exception: they intentionally FAIL on the
broken code. DISTINCT is a feature to add across the lexer, parser, compiler,
VM, disassembler and serialiser. They are exempt from "all examples pass on
pristine". Their `.expected` files show the intended output.

The source lives in `src/`. The test driver lives in `tests/`.
