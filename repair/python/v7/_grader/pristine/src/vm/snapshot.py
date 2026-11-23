"""Binary snapshot format, its checksum and exact restore errors."""

import struct

from . import opcodes as O
from .errors import MiniVMError
from .vm import Fiber, VM

MAGIC = b"MV7"
VERSION = 1

NULL, INT, BOOL, STR, ARRAY = range(5)

OPERANDS = {
    O.PUSH: "value", O.LOAD: "text", O.STORE: "text",
    O.JMP: "u32", O.JZ: "u32", O.ARR: "u32",
    O.FIBER: "fiber", O.SPAWN: "text",
}


def fnv1a(data):
    value = 0x811C9DC5
    for byte in data:
        value = ((value ^ byte) * 0x01000193) & 0xFFFFFFFF
    return value


class Writer:
    def __init__(self):
        self.buf = bytearray()

    def byte(self, value):
        self.buf.append(value)

    def u32(self, value):
        self.buf.extend(struct.pack("<I", value & 0xFFFFFFFF))

    def i64(self, value):
        self.buf.extend(struct.pack("<q", value))

    def text(self, value):
        raw = value.encode("utf-8")
        self.u32(len(raw))
        self.buf.extend(raw)

    def value(self, value):
        if value is None:
            self.byte(NULL)
        elif isinstance(value, bool):
            self.byte(BOOL)
            self.byte(1 if value else 0)
        elif isinstance(value, int):
            self.byte(INT)
            self.i64(value)
        elif isinstance(value, str):
            self.byte(STR)
            self.text(value)
        elif isinstance(value, list):
            self.byte(ARRAY)
            self.u32(len(value))
            for item in value:
                self.value(item)
        else:
            raise TypeError("cannot snapshot value %r" % (value,))

    def operand(self, op, arg):
        kind = OPERANDS.get(op)
        if kind == "value":
            self.value(arg)
        elif kind == "text":
            self.text(arg)
        elif kind == "u32":
            self.u32(0 if arg is None else arg)
        elif kind == "fiber":
            self.text(arg[0])
            self.u32(arg[1])


class Reader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def take(self, count):
        if self.pos + count > len(self.data):
            raise MiniVMError("TRUNCATED")
        chunk = self.data[self.pos:self.pos + count]
        self.pos += count
        return chunk

    def byte(self):
        return self.take(1)[0]

    def u32(self):
        return struct.unpack("<I", self.take(4))[0]

    def i64(self):
        return struct.unpack("<q", self.take(8))[0]

    def text(self):
        return self.take(self.u32()).decode("utf-8")

    def value(self):
        kind = self.byte()
        if kind == NULL:
            return None
        if kind == BOOL:
            return self.byte() != 0
        if kind == INT:
            return self.i64()
        if kind == STR:
            return self.text()
        if kind == ARRAY:
            count = self.u32()
            return [self.value() for _ in range(count)]
        raise MiniVMError("TRUNCATED")

    def operand(self, op):
        kind = OPERANDS.get(op)
        if kind == "value":
            return self.value()
        if kind == "text":
            return self.text()
        if kind == "u32":
            return self.u32()
        if kind == "fiber":
            return (self.text(), self.u32())
        return None


def make_snapshot(vm):
    writer = Writer()
    writer.buf.extend(MAGIC)
    writer.byte(VERSION)
    writer.u32(len(vm.code))
    for op, arg in vm.code:
        writer.byte(op)
        writer.operand(op, arg)
    writer.u32(len(vm.vars))
    for name, value in vm.vars.items():
        writer.value(value)
        writer.text(name)
    writer.u32(len(vm.fibers))
    for fid, fiber in vm.fibers.items():
        writer.u32(fid)
        writer.u32(fiber.pc)
        writer.u32(len(fiber.stack))
        for value in fiber.stack:
            writer.value(value)
    writer.u32(len(vm.ready))
    for fid in vm.ready:
        writer.u32(fid)
    writer.u32(len(vm.blocked))
    for waiter, target in vm.blocked:
        writer.u32(waiter)
        writer.u32(target)
    body = bytes(writer.buf)
    return body + struct.pack("<I", fnv1a(body))


def restore_snapshot(data):
    if len(data) > 3 and data[3] != VERSION:
        raise MiniVMError("BAD_VERSION")
    if len(data) < 3 or bytes(data[:3]) != MAGIC:
        raise MiniVMError("BAD_MAGIC")
    if len(data) < 4:
        raise MiniVMError("TRUNCATED")

    reader = Reader(data)
    reader.pos = 4
    code = []
    for _ in range(reader.u32()):
        op = reader.byte()
        code.append((op, reader.operand(op)))

    globals_ = {}
    for _ in range(reader.u32()):
        name = reader.text()
        globals_[name] = reader.value()

    fibers = {}
    duplicate = False
    for _ in range(reader.u32()):
        fid = reader.u32()
        pc = reader.u32()
        stack = [reader.value() for _ in range(reader.u32())]
        if fid in fibers:
            duplicate = True
        fibers[fid] = Fiber(fid, pc, stack)

    ready = [reader.u32() for _ in range(reader.u32())]
    blocked = []
    for _ in range(reader.u32()):
        blocked.append((reader.u32(), reader.u32()))

    if len(data) - reader.pos != 4:
        raise MiniVMError("TRUNCATED")
    expected = struct.unpack("<I", data[reader.pos:reader.pos + 4])[0]
    if fnv1a(bytes(data[:reader.pos])) != expected:
        raise MiniVMError("BAD_CHECKSUM")
    if duplicate:
        raise MiniVMError("DUPLICATE_FIBER")

    vm = VM(code)
    vm.vars = globals_
    vm.fibers = fibers
    vm.ready = ready
    vm.blocked = blocked
    vm.next_id = max(fibers) + 1 if fibers else 1
    vm.current = fibers.get(ready[0], Fiber(0, 0)) if ready else Fiber(0, 0)
    return vm
