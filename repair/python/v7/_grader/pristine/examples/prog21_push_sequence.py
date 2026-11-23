"""Canonical MiniVM v7 example: prog21_push_sequence."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'let a = [1]; push a, 2; push a, 3; print a;'
sys.stdout.write(run(SOURCE))
