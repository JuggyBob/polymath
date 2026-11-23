"""Canonical MiniVM v7 example: prog28_fiber_basic."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'fiber w { print 1; yield; print 2; } let f = spawn w; print 3; join f; print 4;'
sys.stdout.write(run(SOURCE))
