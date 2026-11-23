"""Canonical MiniVM v7 example: prog20_negative_index."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'let a = [1, 2]; print a[-1]; print a[5];'
sys.stdout.write(run(SOURCE))
