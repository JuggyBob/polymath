"""Canonical MiniVM v7 example: prog37_disasm_distinct."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "src"))
from vm import compile_source, disassemble  # noqa: E402

code = compile_source('print distinct([1, 2]);')
text = disassemble(code)
out = 'DISTINCT' if 'DISTINCT' in text else 'MISSING'
sys.stdout.write(out + '\n')
