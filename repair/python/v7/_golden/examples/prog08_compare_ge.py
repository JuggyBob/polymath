"""Canonical MiniVM v7 example: prog08_compare_ge."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print 3 >= 3; print 2 >= 5;'
sys.stdout.write(run(SOURCE))
