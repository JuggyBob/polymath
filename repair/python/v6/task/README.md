# MiniVM v6

A small interpreted language with a visible pipeline:

```
lexer -> parser -> compiler -> bytecode -> VM -> disassembler -> serialiser
```

The source code lives in `src/vm/`. `vm.run(source)` compiles a program and
returns its stdout as a string. `vm.compile_source(source)`, `vm.VM`,
`vm.disassemble`, `vm.dumps` and `vm.loads` expose the individual stages.

## Run the examples

```
python tests/test_visible.py
```

Each program in `examples/` has a `.expected` file showing the stdout it should
produce. Some also have a `.disasm` file showing the disassembly of the compiled
bytecode. The visible test checks the stdout of every example, its disassembly
when present, and a serialise -> deserialise -> execute round trip for every
example.

## Task

This VM is broken in several ways. Hidden acceptance tests define correctness.
Run the examples to see the intended behaviour. Do not change the example files.

## Examples that fail on the broken implementation

The failures below are observations of the current broken code, not a rule book.
`prog01` to `prog12` pass stdout, disassembly and round-trip checks, except that
`prog02` fails its round-trip check (a string argument containing a space does
not survive the serialiser).

- `prog13`, `prog14`, `prog15`, `prog33`: `distinct` does not execute correctly;
  `prog13` also fails its disassembly check, `prog15` combines `distinct` with
  a spaced string in the round trip, and `prog33` is the round-trip case.
- `prog16`: subtraction; `prog17`: modulo (its disassembly check also fails).
- `prog18`: leading-zero integer literal. `prog19`: `>=`.
- `prog20`: tab indentation. `prog21`: a comment after code.
- `prog22`: `not` next to a comparison. `prog23`: `or` and `and` together.
- `prog24`: `else if`. `prog25`: a trailing comma in an array literal.
- `prog26`: equality of two arrays. `prog27`: a negative array index.
- `prog28`: reading a variable that was never assigned.
- `prog29`: an empty array literal. `prog30`: an empty string as a condition.
- `prog31`: the `\n` escape inside a string. `prog32`: string argument in the
  disassembly check.

Every example above passes on the reference implementation.
