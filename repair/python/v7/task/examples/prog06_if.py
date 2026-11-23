"""Canonical MiniVM v7 example: prog06_if."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'let flag = true; if flag { print "yes"; } else { print "no"; } if false { print "bad"; } print "done";'
sys.stdout.write(run(SOURCE))
