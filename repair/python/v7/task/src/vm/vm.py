"""The stack virtual machine: bytecode execution and deterministic fibers."""

from . import opcodes as O
from .values import deep_key, equal, format_value, truthy


class Fiber:
    __slots__ = ("id", "pc", "stack")

    def __init__(self, fid, pc, stack=None):
        self.id = fid
        self.pc = pc
        self.stack = [] if stack is None else stack


def trunc_div(left, right):
    quotient = abs(left) // abs(right)
    return -quotient if (left < 0) != (right < 0) else quotient


class VM:
    def __init__(self, code):
        self.code = list(code)
        self.vars = {}
        self.fibers = {0: Fiber(0, 0)}
        self.ready = [0]
        self.blocked = []
        self.next_id = 1
        self.out = []
        self.current = self.fibers[0]
        self._switched = False
        self.fiber_table = {}
        for index, (op, arg) in enumerate(self.code):
            if op == O.FIBER:
                self.fiber_table[arg[0]] = (index + 1, arg[1])
        self._dispatch = {
            O.PUSH: self._push, O.LOAD: self._load, O.STORE: self._store,
            O.ADD: self._add, O.SUB: self._sub, O.MUL: self._mul,
            O.DIV: self._div, O.LT: self._lt, O.GT: self._gt,
            O.LE: self._le, O.GE: self._ge, O.EQ: self._eq, O.NE: self._ne,
            O.NEG: self._neg, O.NOT: self._not, O.CONCAT: self._concat,
            O.LEN: self._len, O.ARR: self._arr, O.PUSHITEM: self._pushitem,
            O.GETITEM: self._getitem, O.DISTINCT: self._distinct,
            O.DUP: self._dup, O.POP: self._pop, O.SWAP: self._swap,
            O.JMP: self._jmp, O.JZ: self._jz, O.PRINT: self._print,
            O.HALT: self._halt, O.FIBER: self._fiber, O.SPAWN: self._spawn,
            O.JOIN: self._join,
        }

    def run(self):
        code = self.code
        limit = len(code)
        dispatch = self._dispatch
        while self.ready:
            fid = self.ready.pop(0)
            fiber = self.fibers[fid]
            self.current = fiber
            while fiber.pc < limit:
                op, arg = code[fiber.pc]
                fiber.pc += 1
                self._switched = False
                dispatch[op](arg)
                if self._switched:
                    break
            if fiber.pc >= limit:
                self._wake(fiber.id)
        return "".join(self.out)

    def _wake(self, fid):
        remaining = []
        for waiter, target in self.blocked:
            if target == fid:
                other = self.fibers.get(waiter)
                if other is not None and other.pc < len(self.code):
                    self.ready.append(waiter)
                    continue
            remaining.append((waiter, target))
        self.blocked = remaining

    def push(self, value):
        self.current.stack.append(value)

    def pop(self):
        return self.current.stack.pop()

    def _binary_numbers(self):
        right = self.pop()
        left = self.pop()
        if isinstance(left, bool) or isinstance(right, bool):
            raise TypeError("arithmetic requires integers")
        if not isinstance(left, int) or not isinstance(right, int):
            raise TypeError("arithmetic requires integers")
        return left, right

    def _ordered(self, left, right):
        if isinstance(left, bool) or isinstance(right, bool):
            return None
        if isinstance(left, int) and isinstance(right, int):
            return (left > right) - (left < right)
        if isinstance(left, str) and isinstance(right, str):
            return (left > right) - (left < right)
        return None

    def _compare(self, op):
        right = self.pop()
        left = self.pop()
        value = self._ordered(left, right)
        if op == O.LT:
            self.push(value is not None and value < 0)
        elif op == O.LE:
            self.push(value is not None and value <= 0)
        elif op == O.GT:
            self.push(value is not None and value > 0)
        else:
            self.push(value is not None and value >= 0)

    def _push(self, arg):
        self.push(arg)

    def _load(self, arg):
        self.push(self.vars.get(arg))

    def _store(self, arg):
        self.vars[arg] = self.pop()

    def _add(self, arg):
        right = self.pop()
        left = self.pop()
        if isinstance(left, str) and isinstance(right, str):
            self.push(format_value(left) + format_value(right))
            return
        left, right = self._binary_numbers_from(left, right)
        self.push(left + right)

    def _binary_numbers_from(self, left, right):
        if isinstance(left, bool) or isinstance(right, bool):
            raise TypeError("addition requires integers or strings")
        if not isinstance(left, int) or not isinstance(right, int):
            raise TypeError("addition requires integers or strings")
        return left, right

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
        self.push(trunc_div(left, right))

    def _lt(self, arg):
        self._compare(O.LT)

    def _le(self, arg):
        self._compare(O.LE)

    def _gt(self, arg):
        self._compare(O.GT)

    def _ge(self, arg):
        self._compare(O.GE)

    def _eq(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(equal(left, right))

    def _ne(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(not equal(left, right))

    def _neg(self, arg):
        value = self.pop()
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("negation requires an integer")
        self.push(-value)

    def _not(self, arg):
        self.push(not truthy(self.pop()))

    def _concat(self, arg):
        right = self.pop()
        left = self.pop()
        self.push(format_value(left) + format_value(right))

    def _len(self, arg):
        value = self.pop()
        if isinstance(value, (str, list)):
            self.push(len(value))
        else:
            raise TypeError("len requires a string or array")

    def _arr(self, arg):
        count = arg
        if count:
            stack = self.current.stack
            items = stack[-count:]
            del stack[-count:]
            self.push(items)
        else:
            self.push([])

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
        if not isinstance(array, list) or isinstance(index, bool) or not isinstance(index, int):
            self.push(None)
            return
        self.push(array[index] if -len(array) <= index < len(array) else None)

    def _distinct(self, arg):
        value = self.pop()
        seen = set()
        for item in value:
            key = id(item)
            if key in seen:
                self.push(False)
                return
            seen.add(key)
        self.push(True)

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
        self.current.pc = arg

    def _jz(self, arg):
        if not truthy(self.pop()):
            self.current.pc = arg

    def _print(self, arg):
        self.out = self.out[:] + [format_value(self.pop()) + "\n"]

    def _halt(self, arg):
        self.current.pc = len(self.code)
        self._switched = True

    def _fiber(self, arg):
        name, length = arg
        start = self.current.pc
        self.fiber_table[name] = (start, length)
        self.current.pc = start + length

    def _spawn(self, arg):
        start, _ = self.fiber_table[arg]
        fid = self.next_id
        self.next_id += 1
        self.fibers[fid] = Fiber(fid, start)
        self.ready.append(fid)
        self.push(fid)

    def _yield(self, arg):
        self._switched = True

    def _join(self, arg):
        target = self.pop()
        other = self.fibers.get(target)
        if other is not None:
            self.blocked.append((self.current.id, target))
            self._switched = True
