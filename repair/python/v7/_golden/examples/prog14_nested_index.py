"""Canonical MiniVM v7 example: prog14_nested_index."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'let a = [[1, 2], [3, 4]]; print a[1][0]; print a[0][1];'
sys.stdout.write(run(SOURCE))
