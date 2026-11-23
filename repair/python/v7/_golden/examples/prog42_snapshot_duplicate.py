"""Canonical MiniVM v7 example: prog42_snapshot_duplicate."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "src"))
import struct

from vm import MiniVMError, opcodes as O, restore  # noqa: E402
from vm.snapshot import fnv1a  # noqa: E402

dup_bytes = bytearray(b'MV7' + bytes([1]))
dup_bytes += struct.pack('<I', 1)
dup_bytes += bytes([O.HALT])
dup_bytes += struct.pack('<I', 0)
dup_bytes += struct.pack('<I', 2)
for fid in (7, 7):
    dup_bytes += struct.pack('<I', fid)
    dup_bytes += struct.pack('<I', 0)
    dup_bytes += struct.pack('<I', 0)
dup_bytes += struct.pack('<I', 0)
dup_bytes += struct.pack('<I', 0)
dup_bytes += struct.pack('<I', fnv1a(bytes(dup_bytes)))
bytes_with_duplicate_fiber_ids = bytes(dup_bytes)
try:
    restore(bytes_with_duplicate_fiber_ids)
except MiniVMError as exc:
    out = str(exc) + '\n'
sys.stdout.write(out)
