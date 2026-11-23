// Canonical example: prog26_distinct_basic
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
    std::cout << minivm::run(R"V7SRC(print distinct([1, 2, 3]); print distinct([1, 2, 1]); print distinct([]);)V7SRC");
    return 0;
}
