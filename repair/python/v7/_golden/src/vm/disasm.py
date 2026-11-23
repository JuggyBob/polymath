"""Human readable rendering of compiled bytecode."""

from .opcodes import OP_NAMES


def disassemble(code):
    lines = []
    for index, (op, arg) in enumerate(code):
        name = OP_NAMES.get(op, "?")
        text = "%04X %s" % (index, name)
        if arg is not None:
            text += " " + repr(arg)
        lines.append(text)
    return "\n".join(lines)
