"""Visible acceptance checks for MiniVM v7.

Prints exactly one TEST line per canonical example (prog01..prog45, in
manifest order) and three PERF lines per performance check. Each example is a
Python driver that prints the stdout of one program; its .expected file holds
the exact stdout, byte for byte.
"""

import contextlib
import io
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from vm import VM, disassemble, make_snapshot, restore, run  # noqa: E402
from vm import opcodes as O  # noqa: E402

CANONICAL = [
    "prog01_arith",
    "prog02_strings",
    "prog03_values",
    "prog04_variables",
    "prog05_arrays",
    "prog06_if",
    "prog07_while",
    "prog08_compare_ge",
    "prog09_compare_ne",
    "prog10_escape_nul",
    "prog11_escape_tab",
    "prog12_cmp_chain",
    "prog13_unary_chain",
    "prog14_nested_index",
    "prog15_truthy",
    "prog16_str_cmp",
    "prog17_add_vars",
    "prog18_print_repeat",
    "prog19_len_unicode",
    "prog20_negative_index",
    "prog21_push_sequence",
    "prog22_empty_then",
    "prog23_nested_while",
    "prog24_array3",
    "prog25_null_eq",
    "prog26_distinct_basic",
    "prog27_distinct_types",
    "prog28_fiber_basic",
    "prog29_fiber_yield",
    "prog30_fiber_join_halted",
    "prog31_snapshot_roundtrip",
    "prog32_snapshot_badmagic",
    "prog33_array_alias",
    "prog34_distinct_nested",
    "prog35_str_cmp_unicode",
    "prog36_serial_roundtrip",
    "prog37_disasm_distinct",
    "prog38_snapshot_fibers",
    "prog39_snapshot_badversion",
    "prog40_snapshot_truncated",
    "prog41_snapshot_badchecksum",
    "prog42_snapshot_duplicate",
    "prog43_load_uninit",
    "prog44_stack_ops",
    "prog45_serial_fibers",
]


def check(name, ok):
    print("TEST %s %s" % (name, "PASS" if ok else "FAIL"))


def perf(name, limit_ms, action):
    for _ in range(3):
        start = time.perf_counter()
        try:
            action()
            ok = True
        except Exception:
            ok = False
        elapsed = (time.perf_counter() - start) * 1000.0
        print("PERF %s %.3f %s" % (
            name, elapsed, "PASS" if ok and elapsed <= limit_ms else "FAIL"))


def example_checks():
    folder = os.path.join(ROOT, "examples")
    for name in CANONICAL:
        path = os.path.join(folder, name + ".py")
        with open(path[:-3] + ".expected", "r", encoding="utf-8",
                  newline="") as handle:
            expected = handle.read()
        namespace = {"__name__": "__example__", "__file__": path}
        capture = io.StringIO()
        try:
            with contextlib.redirect_stdout(capture):
                exec(compile(open(path, "r", encoding="utf-8").read(), path, "exec"),
                     namespace)
            got = capture.getvalue()
        except Exception:
            got = "<exception>"
        check(name, got == expected)


def main():
    example_checks()
    perf("perf_print", 900.0, lambda: run(
        "let i = 0; while i < 60000 { print i; set i = i + 1; }"))
    big_code = [(O.PUSH, i) for i in range(20000)] + [(O.HALT, None)]
    perf("perf_disasm", 700.0, lambda: disassemble(big_code))
    snap_code = [(O.PUSH, i % 7) for i in range(199)] + [(O.HALT, None)]
    snap_vm = VM(snap_code)
    for i in range(2000):
        snap_vm.vars["g%d" % i] = i
    perf("perf_snapshot", 700.0, lambda: restore(make_snapshot(snap_vm)))


if __name__ == "__main__":
    main()
