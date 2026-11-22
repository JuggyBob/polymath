// The disassembler renders MOD as "mod", not "div".
// Compile with: cl /EHsc /nologo /Od /Iinclude src\*.cpp examples\mod_disasm.cpp
#include <iostream>

#include "bytecode.h"
#include "disasm.h"

int main() {
    minivm::Bytecode bc;
    minivm::Ins i;
    i.op = minivm::Op::MOD;
    bc.code.push_back(i);
    std::cout << minivm::disassemble(bc);
    return 0;
}
