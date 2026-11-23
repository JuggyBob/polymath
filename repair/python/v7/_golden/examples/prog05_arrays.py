"""Canonical MiniVM v7 example: prog05_arrays."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'let a = [1, 3]; print a; print a[0]; print a[2]; print len(a); push a, 9; print a;'
sys.stdout.write(run(SOURCE))
