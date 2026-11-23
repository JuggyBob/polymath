// Canonical example: prog36_serial_roundtrip
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
    minivm::Bytecode bc = minivm::compile_source(R"V7SRC(print "a" + "b"; print true;)V7SRC");
    std::string wire = minivm::serialize(bc);
    minivm::Bytecode back;
    if (minivm::deserialize(wire, back))
        std::cout << minivm::execute(back).output;
    return 0;
}
