"""Recursive descent parser producing a small tuple based AST."""

from .lexer import tokenize


COMPARE_OPS = {"==", "!=", "<", "<=", ">"}
CALL_NAMES = {"len", "distinct"}


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def peek(self):
        return self.tokens[self.index]

    def advance(self):
        token = self.tokens[self.index]
        self.index += 1
        return token

    def at(self, kind, value=None):
        token = self.peek()
        return token.kind == kind and (value is None or token.value == value)

    def accept(self, kind, value=None):
        if self.at(kind, value):
            return self.advance()
        return None

    def expect(self, kind, value=None):
        token = self.accept(kind, value)
        if token is None:
            got = self.peek()
            raise SyntaxError("expected %r at %d, got %r" % (
                value or kind, got.pos, got.value))
        return token

    def parse_program(self):
        statements = []
        while not self.at("EOF") and not self.at("OP", "}"):
            statements.append(self.parse_statement())
        return statements

    def parse_block(self):
        self.expect("OP", "{")
        statements = self.parse_program()
        self.expect("OP", "}")
        return statements

    def parse_statement(self):
        if self.at("KW", "let") or self.at("KW", "set"):
            keyword = self.advance().value
            name = self.expect("IDENT").value
            self.expect("OP", "=")
            value = self.parse_expression()
            self.expect("OP", ";")
            return (keyword, name, value)
        if self.at("KW", "print"):
            self.advance()
            value = self.parse_expression()
            self.expect("OP", ";")
            return ("print", value)
        if self.at("KW", "push"):
            self.advance()
            array = self.parse_expression()
            self.expect("OP", ",")
            value = self.parse_expression()
            self.expect("OP", ";")
            return ("push", array, value)
        if self.at("KW", "if"):
            return self.parse_if()
        if self.at("KW", "while"):
            self.advance()
            condition = self.parse_expression()
            body = self.parse_block()
            return ("while", condition, body)
        if self.at("KW", "fiber"):
            self.advance()
            name = self.expect("IDENT").value
            body = self.parse_block()
            return ("fiber", name, body)
        if self.at("KW", "join"):
            self.advance()
            target = self.parse_expression()
            self.expect("OP", ";")
            return ("join", target)
        if self.at("KW", "yield"):
            self.advance()
            self.expect("OP", ";")
            return ("yield",)
        value = self.parse_expression()
        self.expect("OP", ";")
        return ("print", value)

    def parse_if(self):
        self.expect("KW", "if")
        condition = self.parse_expression()
        then_body = self.parse_block()
        else_body = []
        if self.accept("KW", "else") is not None:
            else_body = []
        return ("if", condition, then_body, else_body)

    def parse_expression(self):
        return self.parse_equality()

    def parse_equality(self):
        node = self.parse_compare()
        while self.at("OP", "==") or self.at("OP", "!="):
            op = self.advance().value
            node = ("bin", op, node, self.parse_compare())
        return node

    def parse_compare(self):
        node = self.parse_add()
        while self.peek().kind == "OP" and self.peek().value in COMPARE_OPS:
            op = self.advance().value
            node = ("bin", op, node, self.parse_add())
        return node

    def parse_add(self):
        node = self.parse_mul()
        while self.at("OP", "+") or self.at("OP", "-"):
            op = self.advance().value
            node = ("bin", op, node, self.parse_mul())
        return node

    def parse_mul(self):
        node = self.parse_unary()
        while self.at("OP", "*") or self.at("OP", "/"):
            op = self.advance().value
            node = ("bin", op, node, self.parse_unary())
        return node

    def parse_unary(self):
        if self.at("OP", "-") or self.at("OP", "!"):
            op = self.advance().value
            return ("un", op, self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        while self.accept("OP", "[") is not None:
            index = self.parse_expression()
            self.expect("OP", "]")
            node = ("index", index, node)
        return node

    def parse_primary(self):
        token = self.peek()
        if token.kind == "INT":
            self.advance()
            return ("int", token.value)
        if token.kind == "STR":
            self.advance()
            return ("str", token.value)
        if token.kind == "KW":
            if token.value == "true":
                self.advance()
                return ("bool", True)
            if token.value == "false":
                self.advance()
                return ("bool", False)
            if token.value == "null":
                self.advance()
                return ("null",)
            if token.value == "len":
                self.advance()
                self.expect("OP", "(")
                argument = self.parse_expression()
                self.expect("OP", ")")
                return ("call", token.value, [argument])
            if token.value == "spawn":
                self.advance()
                return ("spawn", self.expect("IDENT").value)
        if token.kind == "IDENT":
            self.advance()
            return ("var", token.value)
        if self.accept("OP", "(") is not None:
            node = self.parse_expression()
            self.expect("OP", ")")
            return node
        if self.accept("OP", "[") is not None:
            items = []
            if not self.at("OP", "]"):
                items.append(self.parse_expression())
                while self.accept("OP", ",") is not None:
                    items.append(self.parse_expression())
            self.expect("OP", "]")
            return ("array", items)
        raise SyntaxError("unexpected token %r at %d" % (token.value, token.pos))


def parse(tokens):
    return Parser(tokens).parse_program()


def parse_source(source):
    return parse(tokenize(source))
