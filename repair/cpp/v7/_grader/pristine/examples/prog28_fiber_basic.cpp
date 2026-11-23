// Canonical example: prog28_fiber_basic
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
    std::cout << minivm::run(R"V7SRC(fiber w { print 1; yield; print 2; } let f = spawn w; print 3; join f; print 4;)V7SRC");
    return 0;
}
