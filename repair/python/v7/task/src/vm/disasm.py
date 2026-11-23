"""Human readable rendering of compiled bytecode."""

from .opcodes import OP_NAMES


def disassemble(code):
    result = ""
    for index, (op, arg) in enumerate(code):
        name = OP_NAMES.get(op, "?")
        text = "%04X %s" % (index, name)
        if arg is not None:
            text += " " + repr(arg)
        result = text + "\n" + result
    return "\n".join(reversed(result.rstrip("\n").split("\n")))
