"""Canonical MiniVM v7 example: prog10_escape_nul."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print "a\\0b"; print len("a\\0b");'
sys.stdout.write(run(SOURCE))
