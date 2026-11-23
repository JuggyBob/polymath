// Canonical example: prog21_push_sequence
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
    std::cout << minivm::run(R"V7SRC(let a = [1]; push a, 2; push a, 3; print a;)V7SRC");
    return 0;
}
