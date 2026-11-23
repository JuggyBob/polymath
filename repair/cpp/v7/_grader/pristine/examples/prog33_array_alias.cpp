// Canonical example: prog33_array_alias
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
    std::cout << minivm::run(R"V7SRC(let a = [1]; let b = a; push b, 2; print a; print b;)V7SRC");
    return 0;
}
