// Canonical example: prog44_stack_ops
#include <iostream>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
#include "vm.h"

static minivm::Ins mk(int64_t num, minivm::Op op) {
    minivm::Ins i;
    i.op = op;
    i.num = num;
    return i;
}

int main() {
#ifdef _WIN32
    _setmode(_fileno(stdout), _O_BINARY);
#endif
    minivm::Bytecode bc;
    bc.code.push_back(mk(1, minivm::Op::PUSH));
    bc.code.push_back(mk(0, minivm::Op::DUP));
    bc.code.push_back(mk(0, minivm::Op::ADD));
    bc.code.push_back(mk(0, minivm::Op::PRINT));
    bc.code.push_back(mk(3, minivm::Op::PUSH));
    bc.code.push_back(mk(9, minivm::Op::PUSH));
    bc.code.push_back(mk(0, minivm::Op::SWAP));
    bc.code.push_back(mk(0, minivm::Op::PRINT));
    bc.code.push_back(mk(0, minivm::Op::PRINT));
    bc.code.push_back(mk(0, minivm::Op::HALT));
    std::cout << minivm::execute(bc).output;
    return 0;
}
