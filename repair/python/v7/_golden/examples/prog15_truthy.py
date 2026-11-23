"""Canonical MiniVM v7 example: prog15_truthy."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'if "" { print "x"; } else { print "y"; } if [] { print "a"; } else { print "b"; } if 0 { print "c"; } else { print "d"; }'
sys.stdout.write(run(SOURCE))
