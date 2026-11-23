// Canonical example: prog17_add_vars
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
    std::cout << minivm::run(R"V7SRC(let a = "x"; let b = "y"; print a + b; print "n=" + 5;)V7SRC");
    return 0;
}
