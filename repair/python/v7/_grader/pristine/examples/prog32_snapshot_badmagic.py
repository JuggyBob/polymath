"""Canonical MiniVM v7 example: prog32_snapshot_badmagic."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import MiniVMError, restore  # noqa: E402

try:
    restore(b'XXXX' + b'\x00' * 32)
except MiniVMError as exc:
    out = str(exc) + '\n'
sys.stdout.write(out)
