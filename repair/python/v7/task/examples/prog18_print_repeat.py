"""Canonical MiniVM v7 example: prog18_print_repeat."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print 1; print 1; print 2;'
sys.stdout.write(run(SOURCE))
