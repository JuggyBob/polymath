"""The stack virtual machine that executes compiled bytecode."""

from . import opcodes as O
from .values import deep_key, equal, format_value, truthy


def _trunc_div(left, right):
    quotient = abs(left) // abs(right)
    return -quotient if (left < 0) != (right < 0) else quotient


class VM:
    def __init__(self, code):
        self.code = list(code)
        self.stack = []
        self.vars = {}
        self.ip = 0
        self._out = []
        self._dispatch = {
            O.PUSH: self._push, O.LOAD: self._load, O.STORE: self._store,
            O.ADD: self._add, O.SUB: self._sub, O.MUL: self._mul,
            O.DIV: self._div, O.MOD: self._mod,
            O.EQ: self._eq, O.NE: self._ne, O.LT: self._lt, O.LE: self._le,
            O.GT: self._gt, O.GE: self._ge,
            O.AND: self._and, O.OR: self._or, O.NOT: self._not,
            O.NEG: self._neg, O.CONCAT: self._concat, O.LEN: self._len,
            O.ARR: self._arr, O.PUSHITEM: self._pushitem,
            O.GETITEM: self._getitem, O.SETITEM: self._setitem,
            O.UNIQ: self._uniq, O.DISTINCT: self._distinct,
            O.DUP: self._dup, O.POP: self._pop, O.SWAP: self._swap,
            O.JMP: self._jmp, O.JZ: self._jz, O.PRINT: self._print,
            O.HALT: self._halt,
        }

    def run(self):
        self.stack = []
        self.vars = {}
        self.ip = 0
        self._out = []
        code = self.code
        dispatch = self._dispatch
        while self.ip < len(code):
            op, arg = code[self.ip]
            self.ip += 1
            handler = dispatch.get(op)
            if handler is None:
                raise RuntimeError("unknown opcode %r" % (op,))
            handler(arg)
        return "".join(self._out)

    def pop(self):
        if not self.stack:
            raise RuntimeError("stack underflow")
        return self.stack.pop()

    def push(self, value):
        self.stack.append(value)

    def _binary_numbers(self):
        right = self.pop()
        left = self.pop()
        if isinstance(left, bool) or isinstance(right, bool):
            raise TypeError("arithmetic requires integers")
        if not isinstance(left, int) or not isinstance(right, int):
            raise TypeError("arithmetic requires integers")
        return left, right

    def _push(self, arg):
        self.push(arg)

    def _load(self, arg):
        self.push(self.vars.get(arg, None))

    def _store(self, arg):
        self.vars[arg] = self.pop()

    def _add(self, arg):
        right = self.pop()
        left = self.pop()
        if isinstance(left, str) or isinstance(right, str):
            self.push(format_value(left) + format_value(right))
            return
        if isinstance(left, bool) or isinstance(right, bool):
            raise TypeError("addition requires integers or strings")
        if not isinstance(left, int) or not isinstance(right, int):
            raise TypeError("addition requires integers or strings")
        self.push(left + right)

    def _sub(self, arg):
        left, right = self._binary_numbers()
        self.push(left - right)

    def _mul(self, arg):
        left, right = self._binary_numbers()
        self.push(left * right)

    def _div(self, arg):
        left, right = self._binary_numbers()
        if right == 0:
            raise ZeroDivisionError("division by zero")
        self.push(_trunc_div(left, right))

    def _mod(self, arg):
        left, right = self._binary_numbers()
        if right == 0:
            raise ZeroDivisionError("division by zero")
        self.push(left - _trunc_div(left, right) * right)

    def _eq(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(equal(left, right))

    def _ne(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(not equal(left, right))

    def _ordered(self, left, right):
        if isinstance(left, bool) or isinstance(right, bool):
            left = int(left)
            right = int(right)
        if isinstance(left, int) and isinstance(right, int):
            return (left > right) - (left < right)
        if isinstance(left, str) and isinstance(right, str):
            return (left > right) - (left < right)
        raise TypeError("ordering requires two numbers or two strings")

    def _lt(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(self._ordered(left, right) < 0)

    def _le(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(self._ordered(left, right) <= 0)

    def _gt(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(self._ordered(left, right) > 0)

    def _ge(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(self._ordered(left, right) >= 0)

    def _and(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(bool(truthy(left) and truthy(right)))

    def _or(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(bool(truthy(left) or truthy(right)))

    def _not(self, arg):
        self.push(not truthy(self.pop()))

    def _neg(self, arg):
        value = self.pop()
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("negation requires an integer")
        self.push(-value)

    def _concat(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(format_value(left) + format_value(right))

    def _len(self, arg):
        value = self.pop()
        if isinstance(value, str):
            self.push(len(value))
        elif isinstance(value, list):
            self.push(len(value))
        else:
            raise TypeError("len requires a string or array")

    def _arr(self, arg):
        count = arg
        items = self.stack[-count:] if count else []
        if count:
            del self.stack[-count:]
        self.push(items)

    def _pushitem(self, arg):
        value = self.pop()
        array = self.pop()
        if not isinstance(array, list):
            raise TypeError("push requires an array")
        array.append(value)
        self.push(array)

    def _getitem(self, arg):
        index = self.pop()
        array = self.pop()
        if not isinstance(array, list):
            raise TypeError("get requires an array")
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError("index must be an integer")
        if index < 0:
            index += len(array)
        self.push(array[index] if 0 <= index < len(array) else None)

    def _setitem(self, arg):
        value = self.pop()
        index = self.pop()
        array = self.pop()
        if not isinstance(array, list):
            raise TypeError("set requires an array")
        if index == len(array):
            array.append(value)
        elif 0 <= index < len(array):
            array[index] = value
        self.push(array)

    def _dedupe(self, array):
        seen = set()
        result = []
        for item in array:
            key = deep_key(item)
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

    def _uniq(self, arg):
        self.push(self._dedupe(self.pop()))

    def _distinct(self, arg):
        self.push(self._dedupe(self.pop()))

    def _dup(self, arg):
        value = self.pop()
        self.push(value)
        self.push(value)

    def _pop(self, arg):
        self.pop()

    def _swap(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(right)
        self.push(left)

    def _jmp(self, arg):
        self.ip = arg

    def _jz(self, arg):
        value = self.pop()
        if not truthy(value):
            self.ip = arg

    def _print(self, arg):
        self._out.append(format_value(self.pop()) + "\n")

    def _halt(self, arg):
        self.ip = len(self.code)
