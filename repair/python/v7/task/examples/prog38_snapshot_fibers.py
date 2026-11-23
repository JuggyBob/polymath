"""Canonical MiniVM v7 example: prog38_snapshot_fibers."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "src"))
from vm import MiniVM, restore  # noqa: E402

vm = MiniVM.from_source('fiber a { print 1; yield; print 2; } spawn a; yield;')
out = restore(vm.snapshot()).run()
sys.stdout.write(out)
