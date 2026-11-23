// Canonical example: prog13_unary_chain
#include <iostream>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

#include "vm.h"

int main() {
#ifdef _WIN32
    _setmode(_fileno(stdout), _O_BINARY);
#endif
    std::cout << minivm::run(R"V7SRC(print - - 3; print ! ! true; print -5 / 2;)V7SRC");
    return 0;
}
