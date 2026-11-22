// DISTINCT survives serialize -> deserialize -> execute.
// Compile with: cl /EHsc /nologo /Od /Iinclude src\*.cpp examples\distinct_roundtrip.cpp
#include <iostream>

#include "disasm.h"
#include "serialize.h"
#include "vm.h"

using namespace minivm;

static Ins mk(Op op, int64_t num = 0, const std::string& text = "") {
    Ins i;
    i.op = op;
    i.num = num;
    i.text = text;
    return i;
}

int main() {
    Bytecode bc;
    bc.code.push_back(mk(Op::PUSH, 1));
    bc.code.push_back(mk(Op::PUSH, 2));
    bc.code.push_back(mk(Op::DISTINCT));
    bc.code.push_back(mk(Op::PRINT));
    bc.code.push_back(mk(Op::HALT));

    std::string wire = serialize(bc);
    Bytecode back;
    bool ok = deserialize(wire, back);
    std::cout << (ok ? "ok\n" : "bad\n");
    std::cout << execute(back).output;
    std::cout << disassemble(back);
    return 0;
}
