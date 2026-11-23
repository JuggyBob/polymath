# MiniVM v7

A small interpreted language with a visible pipeline:

```
lexer -> parser -> compiler -> bytecode -> VM -> disassembler -> serialiser
```

The source lives in `src/vm/`. `vm.run(source)` compiles a program and returns
its stdout as a string. `vm.MiniVM`, `vm.compile_source`, `vm.execute`,
`vm.disassemble`, `vm.serialize`, `vm.deserialize`, `vm.snapshot` and `vm.restore`
expose the individual stages.

## Task

This VM is broken in several ways. Hidden acceptance tests define correctness.
Run the examples to see the intended behaviour.

Failures may be masked by earlier faults. After a fix, re-run everything: new
failures are expected and are part of the task.

Do not change the example files. The visible tests and examples are the only
specification.

## Run one example

```
python examples/prog01_arith.py
```

Each example driver prints exactly the stdout stored in its matching `.expected`
file. Drivers import the VM from `../src`.

## Run the visible suite

```
python tests/test_visible.py
```

The suite prints one `TEST <name> PASS|FAIL` line per check and three
`PERF <name> <milliseconds> PASS|FAIL` lines per performance workload.
