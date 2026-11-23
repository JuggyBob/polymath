"""Canonical MiniVM v7 example: prog31_snapshot_roundtrip."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "src"))
from vm import MiniVM, restore  # noqa: E402

vm = MiniVM.from_source('let x = 5; print x + 1;')
b = vm.snapshot()
vm2 = restore(b)
out = vm2.run()
sys.stdout.write(out)
