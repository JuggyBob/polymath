"""Canonical MiniVM v7 example: prog17_add_vars."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'let a = "x"; let b = "y"; print a + b; print "n=" + 5;'
sys.stdout.write(run(SOURCE))
