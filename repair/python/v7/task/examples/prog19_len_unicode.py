"""Canonical MiniVM v7 example: prog19_len_unicode."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print len("é"); print len("abc"); print len("😀");'
sys.stdout.write(run(SOURCE))
