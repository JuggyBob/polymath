"""Canonical MiniVM v7 example: prog36_serial_roundtrip."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "..", "src"))
from vm import compile_source, deserialize, execute, serialize  # noqa: E402

code = compile_source('print "a" + "b"; print true;')
back = deserialize(serialize(code))
out = execute(back)
sys.stdout.write(out)
