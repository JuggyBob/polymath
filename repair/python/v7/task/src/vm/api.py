"""Convenience entry points for the whole pipeline."""

from .compiler import Compiler
from .disasm import disassemble as disassemble_code
from .errors import MiniVMError
from .lexer import tokenize
from .parser import parse
from .serialize import deserialize as deserialize_text
from .serialize import serialize as serialize_code
from .snapshot import make_snapshot, restore_snapshot
from .vm import VM


class MiniVM:
    def __init__(self, code):
        self.code = code
        self.vm = VM(code)

    @classmethod
    def from_source(cls, source):
        return cls(compile_source(source))

    def run(self):
        return self.vm.run()

    def snapshot(self):
        return make_snapshot(self.vm)


def compile_source(source):
    return Compiler().compile(parse(tokenize(source)))


def execute(code):
    return VM(code).run()


def run(source):
    return execute(compile_source(source))


def disassemble(code):
    return disassemble_code(code)


def serialize(code):
    return serialize_code(code)


def deserialize(text):
    return deserialize_text(text)


def snapshot(vm):
    return make_snapshot(vm.vm if isinstance(vm, MiniVM) else vm)


def restore(data):
    return restore_snapshot(data)
