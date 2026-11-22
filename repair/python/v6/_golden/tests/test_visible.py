"""Visible acceptance checks for MiniVM v6.

Prints one TEST line per check and three PERF lines per performance check.
Examples are the specification: each .txt has a .expected stdout, an optional
.disasm rendering of its compiled bytecode, and a round-trip expectation.
"""

import glob
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from vm import VM, compile_source, disassemble, dumps, loads, run  # noqa: E402


def check(name, condition):
    print("TEST %s %s" % (name, "PASS" if condition else "FAIL"))


def perf(name, limit_ms, action):
    for _ in range(3):
        start = time.perf_counter()
        action()
        elapsed = (time.perf_counter() - start) * 1000.0
        print("PERF %s %.3f %s" % (
            name, elapsed, "PASS" if elapsed <= limit_ms else "FAIL"))


def example_checks():
    folder = os.path.join(ROOT, "examples")
    for path in sorted(glob.glob(os.path.join(folder, "*.txt"))):
        base = os.path.basename(path)[:-4]
        source = open(path, "r", encoding="utf-8").read()
        expected = open(path[:-4] + ".expected", "r", encoding="utf-8").read()

        try:
            actual = run(source)
        except Exception:
            actual = "<exception>"
        check("example_" + base, actual == expected)

        disasm_path = path[:-4] + ".disasm"
        if os.path.exists(disasm_path):
            wanted = open(disasm_path, "r", encoding="utf-8").read().rstrip("\n")
            try:
                rendered = disassemble(compile_source(source))
            except Exception:
                rendered = "<exception>"
            check("disasm_" + base, rendered == wanted)

        try:
            code = compile_source(source)
            revived = loads(dumps(code))
            roundtrip_output = VM(revived).run()
        except Exception:
            revived = "<exception>"
            roundtrip_output = "<exception>"
        check("roundtrip_" + base,
              revived != "<exception>" and roundtrip_output == expected)


def pipeline_checks():
    source = "let x = 1;\nlet x = x + 2;\nprint(x);\n"
    code = compile_source(source)
    text = disassemble(code)
    check("vis_disasm_simple",
          text.startswith("0000 PUSH 1") and " ADD" in text
          and " PRINT" in text and text.endswith("HALT"))
    revived = loads(dumps(code))
    check("vis_roundtrip_simple",
          revived == code and VM(revived).run() == run(source))


def main():
    example_checks()
    pipeline_checks()
    source = "let i = 0;\nlet s = 0;\nwhile i < 20 {\n let s = s + i;\n let i = i + 1;\n}\nprint(s);\n"
    perf("perf_vis_small", 1000.0, lambda: run(source))


if __name__ == "__main__":
    main()
