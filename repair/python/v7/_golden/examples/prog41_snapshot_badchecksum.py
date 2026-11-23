"""Canonical MiniVM v7 example: prog41_snapshot_badchecksum."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "src"))
from vm import MiniVM, MiniVMError, restore  # noqa: E402

good_bytes = MiniVM.from_source('let x = 5; print x + 1;').snapshot()
try:
    restore(good_bytes[:-1] + bytes([good_bytes[-1] ^ 1]))
except MiniVMError as exc:
    out = str(exc) + '\n'
sys.stdout.write(out)
