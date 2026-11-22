// Serialising a second bytecode starts from an empty buffer.
// Compile with: cl /EHsc /nologo /Od /Iinclude src\*.cpp examples\serialize_repeat.cpp
#include <iostream>

#include "bytecode.h"
#include "serialize.h"

using namespace minivm;

static Ins mk(Op op, int64_t num) {
    Ins i;
    i.op = op;
    i.num = num;
    return i;
}

int main() {
    Bytecode a;
    a.code.push_back(mk(Op::PUSH, 1));
    std::cout << serialize(a);
    Bytecode b;
    b.code.push_back(mk(Op::PUSH, 2));
    std::cout << "---\n" << serialize(b);
    return 0;
}
