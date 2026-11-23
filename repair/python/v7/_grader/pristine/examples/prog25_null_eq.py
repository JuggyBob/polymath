"""Canonical MiniVM v7 example: prog25_null_eq."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import run  # noqa: E402

SOURCE = 'print null == null; print null != 0; print null == false;'
sys.stdout.write(run(SOURCE))
