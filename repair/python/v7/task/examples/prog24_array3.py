"""Canonical MiniVM v7 example: prog24_array3."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print [1, 2, 3]; print []; print [[1], [2, 3]];'
sys.stdout.write(run(SOURCE))
