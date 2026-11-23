"""Compiler: turns the AST into a flat list of (opcode, argument) pairs."""

from . import opcodes as O


BINARY_OPS = {
    "+": O.ADD, "-": O.SUB, "*": O.MUL, "/": O.DIV,
    "<": O.LT, ">": O.GT, "<=": O.LE, ">=": O.GE,
    "==": O.EQ, "!=": O.NE,
}


class Compiler:
    def __init__(self):
        self.code = []

    def emit(self, op, arg=None):
        self.code.append((op, arg))
        return len(self.code) - 1

    def patch(self, index, arg):
        op, _ = self.code[index]
        self.code[index] = (op, arg)

    def compile(self, statements):
        for statement in statements:
            self.compile_statement(statement)
        self.emit(O.HALT)
        return self.code

    def compile_statement(self, node):
        kind = node[0]
        if kind == "let" or kind == "set":
            self.compile_expression(node[2])
            self.emit(O.STORE, node[1])
        elif kind == "print":
            self.compile_expression(node[1])
            self.emit(O.PRINT)
        elif kind == "push":
            self.compile_expression(node[1])
            self.compile_expression(node[2])
            self.emit(O.PUSHITEM)
            self.emit(O.POP)
        elif kind == "exprstmt":
            self.compile_expression(node[1])
            self.emit(O.POP)
        elif kind == "if":
            _, condition, then_body, else_body = node
            self.compile_expression(condition)
            jump_false = self.emit(O.JZ, None)
            for statement in then_body:
                self.compile_statement(statement)
            jump_end = self.emit(O.JMP, None)
            self.patch(jump_false, len(self.code))
            for statement in else_body:
                self.compile_statement(statement)
            self.patch(jump_end, len(self.code))
        elif kind == "while":
            _, condition, body = node
            start = len(self.code)
            self.compile_expression(condition)
            jump_false = self.emit(O.JZ, None)
            for statement in body:
                self.compile_statement(statement)
            self.emit(O.JMP, start)
            self.patch(jump_false, len(self.code))
        elif kind == "fiber":
            _, name, body = node
            header = self.emit(O.FIBER, (name, 0))
            start = len(self.code)
            for statement in body:
                self.compile_statement(statement)
            self.emit(O.HALT)
            self.patch(header, (name, len(self.code) - start))
        elif kind == "join":
            self.compile_expression(node[1])
            self.emit(O.JOIN)
        elif kind == "yield":
            self.emit(O.YIELD)
        else:
            raise ValueError("unknown statement %r" % (kind,))

    def compile_expression(self, node):
        kind = node[0]
        if kind in ("int", "str", "bool", "null"):
            self.emit(O.PUSH, node[1] if len(node) > 1 else None)
        elif kind == "var":
            self.emit(O.LOAD, node[1])
        elif kind == "spawn":
            self.emit(O.SPAWN, node[1])
        elif kind == "array":
            for item in node[1]:
                self.compile_expression(item)
            self.emit(O.ARR, len(node[1]))
        elif kind == "index":
            self.compile_expression(node[1])
            self.compile_expression(node[2])
            self.emit(O.GETITEM)
        elif kind == "un":
            self.compile_expression(node[2])
            self.emit(O.NEG if node[1] == "-" else O.NOT)
        elif kind == "bin":
            self.compile_expression(node[2])
            self.compile_expression(node[3])
            self.emit(BINARY_OPS[node[1]])
        elif kind == "call":
            self.compile_expression(node[2][0])
            self.emit(O.LEN if node[1] == "len" else O.DISTINCT)
        else:
            raise ValueError("unknown expression %r" % (kind,))
