// Canonical example: prog24_array3
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
    std::cout << minivm::run(R"V7SRC(print [1, 2, 3]; print []; print [[1], [2, 3]];)V7SRC");
    return 0;
}
