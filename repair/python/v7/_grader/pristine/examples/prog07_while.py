"""Canonical MiniVM v7 example: prog07_while."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'let i = 0; while i < 3 { print i; set i = i + 1; }'
sys.stdout.write(run(SOURCE))
