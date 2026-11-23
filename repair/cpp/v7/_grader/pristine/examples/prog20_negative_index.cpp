// Canonical example: prog20_negative_index
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
    std::cout << minivm::run(R"V7SRC(let a = [1, 2]; print a[-1]; print a[5];)V7SRC");
    return 0;
}
