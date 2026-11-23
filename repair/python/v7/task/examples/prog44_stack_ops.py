"""Canonical MiniVM v7 example: prog44_stack_ops."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "src"))
from vm import execute, opcodes as O  # noqa: E402

code = [(O.PUSH, 1), (O.DUP, None), (O.ADD, None), (O.PRINT, None),
        (O.PUSH, 3), (O.PUSH, 9), (O.SWAP, None), (O.PRINT, None),
        (O.PRINT, None), (O.HALT, None)]
out = execute(code)
sys.stdout.write(out)
