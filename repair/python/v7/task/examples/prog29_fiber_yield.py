"""Canonical MiniVM v7 example: prog29_fiber_yield."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'fiber a { print "a1"; yield; print "a2"; } fiber b { print "b1"; yield; print "b2"; } spawn a; spawn b; yield; yield;'
sys.stdout.write(run(SOURCE))
