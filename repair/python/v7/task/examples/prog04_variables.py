"""Canonical MiniVM v7 example: prog04_variables."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'let a = 4; let b = a + 3; set b = b * 2; print a; print b;'
sys.stdout.write(run(SOURCE))
