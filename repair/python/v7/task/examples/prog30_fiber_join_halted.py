"""Canonical MiniVM v7 example: prog30_fiber_join_halted."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'fiber w { print 7; } let f = spawn w; yield; join f; print 8;'
sys.stdout.write(run(SOURCE))
