// Canonical example: prog37_disasm_distinct
#include <iostream>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
#include "disasm.h"
#include "vm.h"

int main() {
#ifdef _WIN32
    _setmode(_fileno(stdout), _O_BINARY);
#endif
    minivm::Bytecode bc = minivm::compile_source(R"V7SRC(print distinct([1, 2]);)V7SRC");
    std::string text = minivm::disassemble(bc);
    std::cout << (text.find("DISTINCT") != std::string::npos ? "DISTINCT\n" : "MISSING\n");
    return 0;
}
