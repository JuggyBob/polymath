// Canonical example: prog29_fiber_yield
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
    std::cout << minivm::run(R"V7SRC(fiber a { print "a1"; yield; print "a2"; } fiber b { print "b1"; yield; print "b2"; } spawn a; spawn b; yield; yield;)V7SRC");
    return 0;
}
