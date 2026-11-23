"""Canonical MiniVM v7 example: prog34_distinct_nested."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print distinct([[1], [1]]); print distinct([[1], [2]]);'
sys.stdout.write(run(SOURCE))
