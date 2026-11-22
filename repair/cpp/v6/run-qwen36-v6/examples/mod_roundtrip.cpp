// MOD survives a serialise/deserialise cycle and still executes.
// Compile with: cl /EHsc /nologo /Od /Iinclude src\*.cpp examples\mod_roundtrip.cpp
#include <iostream>

#include "serialize.h"
#include "vm.h"

using namespace minivm;

static Ins mk(Op op, int64_t num = 0) {
    Ins i;
    i.op = op;
    i.num = num;
    return i;
}

int main() {
    Bytecode bc;
    bc.code.push_back(mk(Op::PUSH, 6));
    bc.code.push_back(mk(Op::PUSH, 4));
    bc.code.push_back(mk(Op::MOD));
    bc.code.push_back(mk(Op::PRINT));
    bc.code.push_back(mk(Op::HALT));
    Bytecode back;
    if (!deserialize(serialize(bc), back)) {
        std::cout << "bad\n";
        return 0;
    }
    std::cout << execute(back).output;
    return 0;
}
