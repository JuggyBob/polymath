// Canonical example: prog45_serial_fibers
#include <iostream>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif
#include "serialize.h"
#include "vm.h"

int main() {
#ifdef _WIN32
    _setmode(_fileno(stdout), _O_BINARY);
#endif
    minivm::Bytecode bc = minivm::compile_source(R"V7SRC(fiber a { print 1; } spawn a; join 1; print 2;)V7SRC");
    std::string wire = minivm::serialize(bc);
    minivm::Bytecode back;
    if (minivm::deserialize(wire, back))
        std::cout << minivm::execute(back).output;
    return 0;
}
