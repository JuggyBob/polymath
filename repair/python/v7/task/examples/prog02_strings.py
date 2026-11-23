"""Canonical MiniVM v7 example: prog02_strings."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print "hello"; print "a" + "b" + "c"; print "x" + 7; print len("abcd"); print "line1\\nline2"; print "q\\"q"; print "back\\\\slash";'
sys.stdout.write(run(SOURCE))
