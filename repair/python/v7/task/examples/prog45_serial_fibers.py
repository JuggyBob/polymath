"""Canonical MiniVM v7 example: prog45_serial_fibers."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "src"))
from vm import compile_source, deserialize, execute, serialize  # noqa: E402

code = compile_source('fiber a { print 1; } spawn a; join 1; print 2;')
back = deserialize(serialize(code))
out = execute(back)
sys.stdout.write(out)
