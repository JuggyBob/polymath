// The disassembler must render DISTINCT with its own token.
// Compile with: cl /EHsc /nologo /Od /Iinclude src\*.cpp examples\distinct_disasm.cpp
#include <iostream>

#include "compiler.h"
#include "disasm.h"
#include "lexer.h"
#include "parser.h"

int main() {
    using namespace minivm;
    Bytecode bc = compile(parse(lex(
        "push 1\npush 2\ndistinct\nprint\nhalt\n")));
    std::cout << disassemble(bc);
    return 0;
}
