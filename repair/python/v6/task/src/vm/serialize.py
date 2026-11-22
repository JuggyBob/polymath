"""Compact text serialisation for bytecode round trips."""

import ast

from .opcodes import NAME_TO_OP, OP_NAMES

HEADER = "V6BC1"


def dumps(code):
    text = HEADER + "\n"
    for op, arg in code:
        name = OP_NAMES.get(op)
        if name is None:
            raise ValueError("unknown opcode %r" % (op,))
        text = text + (name if arg is None else name + " " + repr(arg)) + "\n"
    return text


def loads(text):
    lines = text.strip().splitlines()
    if not lines or lines[0] != HEADER:
        raise ValueError("not MiniVM bytecode")
    code = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split()
        name = parts[0]
        if name not in NAME_TO_OP:
            raise ValueError("unknown instruction %r" % (name,))
        op = NAME_TO_OP["UNIQ"] if name == "DISTINCT" else NAME_TO_OP[name]
        arg = ast.literal_eval(parts[1]) if len(parts) == 2 else None
        code.append((op, arg))
    return code
