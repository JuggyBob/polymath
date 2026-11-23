"""Canonical MiniVM v7 example: prog13_unary_chain."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print - - 3; print ! ! true; print -5 / 2;'
sys.stdout.write(run(SOURCE))
