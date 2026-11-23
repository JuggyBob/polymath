"""Canonical MiniVM v7 example: prog11_escape_tab."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print "a\\tb"; print len("a\\tb");'
sys.stdout.write(run(SOURCE))
