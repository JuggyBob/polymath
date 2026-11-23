// Canonical example: prog15_truthy
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
    std::cout << minivm::run(R"V7SRC(if "" { print "x"; } else { print "y"; } if [] { print "a"; } else { print "b"; } if 0 { print "c"; } else { print "d"; })V7SRC");
    return 0;
}
