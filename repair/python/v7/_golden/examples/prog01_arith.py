"""Canonical MiniVM v7 example: prog01_arith."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print 2 + 3 * 4; print (2 + 3) * 4; print 10 - 3 - 2; print 7 / 2; print -5 + 9;'
sys.stdout.write(run(SOURCE))
