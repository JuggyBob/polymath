"""Compiler: turns the AST into a flat list of (opcode, argument) pairs."""

from . import opcodes as O


BINARY_OPS = {
    "+": O.ADD, "-": O.SUB, "*": O.MUL, "/": O.DIV, "%": O.MOD,
    "==": O.EQ, "!=": O.NE, "<": O.LT, "<=": O.LE, ">": O.GT, ">=": O.GE,
}


class Compiler:
    def __init__(self):
        self.code = []
        self._last_patch = None

    def emit(self, op, arg=None):
        self.code.append((op, arg))
        return len(self.code) - 1

    def patch(self, index, target):
        op, _ = self.code[index]
        self.code[index] = (op, target)

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
            self._last_patch = jump_false
            self.patch(self._last_patch, len(self.code))
        else:
            raise ValueError("unknown statement %r" % (kind,))

    def compile_expression(self, node):
        kind = node[0]
        if kind == "int" or kind == "str" or kind == "bool" or kind == "null":
            self.emit(O.PUSH, node[1] if len(node) > 1 else None)
        elif kind == "var":
            self.emit(O.LOAD, node[1])
        elif kind == "array":
            for item in node[1]:
                self.compile_expression(item)
            self.emit(O.ARR, len(node[1]))
        elif kind == "un":
            self.compile_expression(node[2])
            self.emit(O.NOT if node[1] == "not" else O.NEG)
        elif kind == "bin":
            op = node[1]
            if op == "and":
                self.compile_short_and(node[2], node[3])
            elif op == "or":
                self.compile_short_or(node[2], node[3])
            else:
                self.compile_expression(node[2])
                self.compile_expression(node[3])
                self.emit(BINARY_OPS[op])
        elif kind == "call":
            self.compile_call(node[1], node[2])
        else:
            raise ValueError("unknown expression %r" % (kind,))

    def compile_short_and(self, left, right):
        self.compile_expression(left)
        self.emit(O.DUP)
        jump_false = self.emit(O.JZ, None)
        self.compile_expression(right)
        self.emit(O.AND)
        jump_end = self.emit(O.JMP, None)
        self.patch(jump_false, len(self.code))
        self.emit(O.POP)
        self.emit(O.PUSH, False)
        self.patch(jump_end, len(self.code))

    def compile_short_or(self, left, right):
        self.compile_expression(left)
        self.emit(O.DUP)
        jump_rhs = self.emit(O.JZ, None)
        self.emit(O.POP)
        self.emit(O.PUSH, True)
        jump_end = self.emit(O.JMP, None)
        self.patch(jump_rhs, len(self.code))
        self.compile_expression(right)
        self.emit(O.OR)
        self.patch(jump_end, len(self.code))

    def compile_call(self, name, args):
        if name == "uniq":
            self.compile_expression(args[0])
            self.emit(O.UNIQ)
        elif name == "distinct":
            self.compile_expression(args[0])
            self.emit(O.DISTINCT)
        elif name == "len":
            self.compile_expression(args[0])
            self.emit(O.LEN)
        elif name == "push":
            self.compile_expression(args[0])
            self.compile_expression(args[1])
            self.emit(O.PUSHITEM)
        elif name == "get":
            self.compile_expression(args[0])
            self.compile_expression(args[1])
            self.emit(O.GETITEM)
        elif name == "concat":
            self.compile_expression(args[0])
            self.compile_expression(args[1])
            self.emit(O.CONCAT)
        else:
            raise ValueError("unknown call %r" % (name,))
