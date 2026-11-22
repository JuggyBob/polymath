"""Convenience entry points for the whole pipeline."""

from .compiler import Compiler
from .lexer import tokenize
from .parser import parse
from .vm import VM


def compile_source(source):
    return Compiler().compile(parse(tokenize(source)))


def execute(code):
    return VM(code).run()


def run(source):
    return execute(compile_source(source))
