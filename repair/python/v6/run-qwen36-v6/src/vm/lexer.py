"""Lexer for the small MiniVM source language."""

KEYWORDS = {
    "let", "set", "print", "if", "else", "while", "true", "false", "null",
    "not", "and", "or", "uniq", "distinct",
}

TWO_CHAR = ("==", "!=", "<=", ">=")
ONE_CHAR = set("+-*/%<>=;,(){}[]")

ESCAPES = {"t": "\t", "r": "\r", "n": "\n", "\\": "\\", '"': '"'}


class Token:
    __slots__ = ("kind", "value", "pos")

    def __init__(self, kind, value, pos):
        self.kind = kind
        self.value = value
        self.pos = pos

    def __repr__(self):
        return "Token(%r, %r, %d)" % (self.kind, self.value, self.pos)


def tokenize(source):
    tokens = []
    i = 0
    n = len(source)
    while i < n:
        c = source[i]
        if c in " \r\n\t":
            i += 1
            continue
        if c == "#":
            while i < n and source[i] != "\n":
                i += 1
            continue
        if c.isdigit():
            start = i
            while i < n and source[i].isdigit():
                i += 1
            tokens.append(Token("INT", int(source[start:i].lstrip("0") or "0"), start))
            continue
        if c.isalpha() or c == "_":
            start = i
            while i < n and (source[i].isalnum() or source[i] == "_"):
                i += 1
            word = source[start:i]
            kind = "KW" if word in KEYWORDS else "IDENT"
            tokens.append(Token(kind, word, start))
            continue
        if c == '"':
            start = i
            i += 1
            chars = []
            while i < n and source[i] != '"':
                if source[i] == "\\" and i + 1 < n:
                    nxt = source[i + 1]
                    chars.append(ESCAPES.get(nxt, nxt))
                    i += 2
                else:
                    chars.append(source[i])
                    i += 1
            if i >= n:
                raise SyntaxError("unterminated string at %d" % start)
            i += 1
            tokens.append(Token("STR", "".join(chars), start))
            continue
        two = source[i:i + 2]
        if two in TWO_CHAR:
            tokens.append(Token("OP", two, i))
            i += 2
            continue
        if c in ONE_CHAR:
            tokens.append(Token("OP", c, i))
            i += 1
            continue
        raise SyntaxError("unexpected character %r at %d" % (c, i))
    tokens.append(Token("EOF", None, n))
    return tokens
