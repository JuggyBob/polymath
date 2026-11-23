// Canonical example: prog34_distinct_nested
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
    std::cout << minivm::run(R"V7SRC(print distinct([[1], [1]]); print distinct([[1], [2]]);)V7SRC");
    return 0;
}
