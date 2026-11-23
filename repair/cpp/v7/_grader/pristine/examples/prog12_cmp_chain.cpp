// Canonical example: prog12_cmp_chain
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
    std::cout << minivm::run(R"V7SRC(print 1 < 2 == true; print 2 <= 2 == true;)V7SRC");
    return 0;
}
