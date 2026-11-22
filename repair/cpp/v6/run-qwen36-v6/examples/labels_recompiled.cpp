// Compiling a second program must not reuse labels from the first one.
// Compile with: cl /EHsc /nologo /Od /Iinclude src\*.cpp examples\labels_recompiled.cpp
#include <iostream>

#include "compiler.h"
#include "disasm.h"
#include "lexer.h"
#include "parser.h"
#include "vm.h"

int main() {
    using namespace minivm;
    std::string first = "push 1\npush 2\npush 3\nghost:\nhalt\n";
    std::string second = "push 0\njz ghost\npush 8\nprint\nhalt\n";

    std::cout << "[" << run(first) << "][" << run(second) << "]\n";
    Bytecode bc = compile(parse(lex(second)));
    std::cout << disassemble(bc);
    return 0;
}
