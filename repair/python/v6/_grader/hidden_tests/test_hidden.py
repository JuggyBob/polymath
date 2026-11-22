"""Hidden acceptance tests for MiniVM v6.

Correctness lines: TEST <name> PASS|FAIL
Performance lines: PERF <name> <milliseconds> PASS|FAIL  (three runs each)
"""

import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from vm import VM, compile_source, disassemble, dumps, loads, run  # noqa: E402


def report(name, ok):
    print("TEST %s %s" % (name, "PASS" if ok else "FAIL"))


def run_case(name, source, expected):
    try:
        actual = run(source)
    except Exception as exc:
        actual = "<%s: %s>" % (type(exc).__name__, exc)
    report(name, actual == expected)


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


def main():
    run_case("h_sub", "print(10 - 4);\nprint(3 - 7);\n", "6\n-4\n")
    run_case("h_mod", "print(10 % 3);\nprint(8 % 4);\n", "1\n0\n")
    run_case("h_ge", "print(3 >= 3);\nprint(2 >= 4);\n", "true\nfalse\n")
    run_case("h_tab_ws", "\tlet a = 4;\n\tprint(a);\n", "4\n")
    run_case("h_trailing_comment", "let a = 7;\nprint(a); # done\n", "7\n")
    run_case("h_leading_zero", "print(007);\n", "7\n")
    run_case("h_not_precedence", "print(not 1 > 2);\n", "true\n")
    run_case("h_else_if",
             'let x = 2;\nif x == 1 {\n print("a");\n} else if x == 2 {\n'
             ' print("b");\n} else {\n print("c");\n}\n', "b\n")
    run_case("h_trailing_comma", "print([1, 2,]);\n", "[1, 2]\n")
    run_case("h_and_or_precedence", "print(true or false and false);\n", "true\n")
    run_case("h_array_eq",
             "print([1, 2] == [1, 2]);\nprint([1] == [2]);\n", "true\nfalse\n")
    run_case("h_unicode_len", 'print(len("héllo"));\n', "5\n")
    run_case("h_neg_index",
             "let a = [10, 20];\npush(a, 30);\nprint(get(a, -1));\n", "30\n")
    run_case("h_not_zero", "print(not 0);\nprint(not 3);\n", "true\nfalse\n")
    run_case("h_undefined_var", "print(missing);\n", "null\n")
    run_case("h_distinct_exec",
             "let a = [3, 1, 3, 2];\nprint(distinct(a));\n", "[3, 1, 2]\n")

    try:
        code = compile_source('let s = "a b";\nprint(s);\n')
        got = VM(loads(dumps(code))).run()
    except Exception:
        got = "<exception>"
    report("h_roundtrip_space", got == "a b\n")

    run_case("h_two_loops",
             "let i = 0;\nlet s = 0;\nwhile i < 2 {\n let s = s + 1;\n"
             " let i = i + 1;\n}\nlet j = 0;\nwhile j < 3 {\n"
             " let s = s + 10;\n let j = j + 1;\n}\nprint(s);\n", "32\n")
    run_case("h_empty_array", "print([]);\n", "[]\n")
    run_case("h_distinct_nested",
             "let a = [[1], [1], [2]];\nprint(distinct(a));\n", "[[1], [2]]\n")
    run_case("h_string_newline", 'print("a\\nb");\n', "a\nb\n")
    run_case("h_bool_array", "print([true, false]);\n", "[true, false]\n")
    run_case("h_null_array", "print([null, 1]);\n", "[null, 1]\n")
    run_case("h_string_array", 'print(["a", "b"]);\n', "[a, b]\n")
    run_case("h_empty_string",
             'if "" {\n print("t");\n} else {\n print("f");\n}\n', "f\n")

    try:
        text = disassemble(compile_source("let a = [3, 1];\nprint(distinct(a));\n"))
    except Exception:
        text = ""
    report("h_distinct_disasm", " DISTINCT" in text)

    try:
        code = compile_source("let a = [2, 1, 2];\nprint(distinct(a));\n")
        got = VM(loads(dumps(code))).run()
    except Exception:
        got = "<exception>"
    report("h_distinct_roundtrip", got == "[2, 1]\n")

    try:
        text = disassemble(compile_source('print("hi");\n'))
    except Exception:
        text = ""
    report("h_disasm_string", "PUSH 'hi'" in text)

    try:
        text = disassemble(compile_source("print(10 % 3);\n"))
    except Exception:
        text = ""
    report("h_mod_disasm", " MOD" in text)

    loop_source = ("let i = 0;\nlet s = 0;\nwhile i < 6000 {\n"
                   " let s = s + i;\n let i = i + 1;\n}\nprint(s);\n")
    perf("perf_vm_dispatch", 100.0, lambda: run(loop_source))

    from vm import opcodes as O  # noqa: E402
    big_code = [(O.PUSH, i) for i in range(60000)] + [(O.HALT, None)]
    perf("perf_serialize", 750.0, lambda: loads(dumps(big_code)))


if __name__ == "__main__":
    main()
