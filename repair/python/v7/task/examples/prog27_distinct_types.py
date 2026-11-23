"""Canonical MiniVM v7 example: prog27_distinct_types."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print distinct(["a", "b"]); print distinct([true, false, true]); print distinct([1, "1"]);'
sys.stdout.write(run(SOURCE))
