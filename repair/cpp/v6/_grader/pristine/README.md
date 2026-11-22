# C++ repair v6 — task

This VM is broken in several ways. Hidden acceptance tests define correctness.
Run the examples to see the intended behaviour. Do not change the example files.

```
cl /EHsc /nologo /Od /Iinclude src\*.cpp tests\test_visible.cpp
test_visible.exe
```

`include/` and `tests/` are frozen. Each `examples/progNN*.txt` is a program for
the little language; its `.expected` file is the stdout it should produce. The
`examples/*.cpp` files are small programs against the public API; compile them
the same way, replacing `tests\test_visible.cpp` with the example file.

Every hidden behaviour has a visible example demonstrating it, including the
`distinct` operation. Some examples fail on the starting source because the
bug affects that whole input class; section "Examples that fail on the starting
source" lists them. Do not change the example files.

## Examples that fail on the starting source

The first twelve programs (`prog01` … `prog12`) already produce their expected
output. The following examples describe behaviour whose output is wrong for
*every* input of that kind, so they do **not** pass on the starting source. Their
`.expected` files are the specification; each one isolates one behaviour.

| Example | Expected behaviour the starting source gets wrong |
|---|---|
| `prog13_distinct_equal` | `distinct` on two equal values prints `false` |
| `prog14_distinct_different` | `distinct` on two different values prints `true` |
| `distinct_pipeline.cpp` | the lexer, parser and compiler each carry a `distinct` layer through to opcode `distinct` |
| `distinct_disasm.cpp` | the disassembler renders the opcode as `distinct` |
| `distinct_roundtrip.cpp` | `distinct` survives serialize → deserialize → execute |
| `prog15_truthy_negative` | a negative integer is truthy, so `jz` does not jump |
| `prog16_escape_newline` | `\n` inside a quoted string is one newline character (length 3, printed on two lines) |
| `prog17_hash_in_string` | `#` inside a quoted string is data, not a comment |
| `prog18_label_case` | label names are case-insensitive (`jz Ll` reaches `LL:`) |
| `labels_recompiled.cpp` | compiling a second program does not reuse labels from the first; an undefined label resolves to instruction 0 |
| `prog19_len_null` | `len` of null is `0` |
| `prog20_div_zero` | division by zero returns `null`, for positive and negative numerators |
| `prog21_swap_single` | `swap` on a one-item stack pads with null, so two swaps leave null on top |
| `prog22_sub_saturates` | subtraction saturates at the signed 64-bit minimum |
| `prog23_mul_saturates` | multiplication saturates at the signed 64-bit maximum |
| `prog24_to_int_clamps` | a literal wider than 64 bits clamps to the signed 64-bit maximum |
| `prog25_null_not_zero` | `null` is not equal to the integer `0` |
| `prog26_ge_equal` | `ge` is true for equal operands |
| `prog27_neq` | `neq` is the negation of `eq` |
| `align_exact.cpp` | `align_up` leaves an already-aligned size unchanged |
| `move_assign.cpp` | move assignment marks the source as moved-from |
| `variables_isolated.cpp` | a fresh `run` does not see variables from an earlier `run` |
| `serialize_repeat.cpp` | a second `serialize` call starts from an empty buffer |
| `mod_roundtrip.cpp` | `MOD` survives serialize → deserialize → execute |
| `mod_disasm.cpp` | the disassembler renders `MOD` as `mod` |

The visible tests in `tests/` are a subset of these behaviours and all pass on
the starting source; they are not a full specification.
