"""Canonical MiniVM v7 example: prog03_values."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print true; print false; print null; print !true; print !0; print 1 < 2; print 2 <= 2; print 3 > 1; print 2 == 2;'
sys.stdout.write(run(SOURCE))
