"""Canonical MiniVM v7 example: prog22_empty_then."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'if true { } else { print "e"; } while false { print "z"; } print "ok";'
sys.stdout.write(run(SOURCE))
