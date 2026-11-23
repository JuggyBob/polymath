"""Compact text serialisation for bytecode round trips."""

import ast

from .opcodes import NAME_TO_OP, OP_NAMES

HEADER = "V7BC1"


def serialize(code):
    lines = [HEADER]
    for op, arg in code:
        name = OP_NAMES.get(op)
        if name is None:
            raise ValueError("unknown opcode %r" % (op,))
        lines.append(name if isinstance(arg, int) else name + " " + repr(arg))
    return "\n".join(lines) + "\n"


def deserialize(text):
    lines = text.strip().splitlines()
    if not lines or lines[0] != HEADER:
        raise ValueError("not MiniVM bytecode")
    code = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split(None, 1)
        name = parts[0]
        if name not in NAME_TO_OP:
            raise ValueError("unknown instruction %r" % (name,))
        op = NAME_TO_OP[name]
        arg = ast.literal_eval(parts[0]) if len(parts) == 2 else None
        code.append((op, arg))
    return code
