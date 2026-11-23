"""Canonical MiniVM v7 example: prog43_load_uninit."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "src"))
from vm import execute, opcodes as O  # noqa: E402

code = [(O.LOAD, 0), (O.PRINT, None), (O.HALT, None)]
out = execute(code)
sys.stdout.write(out)
