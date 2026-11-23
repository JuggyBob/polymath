// Canonical example: prog06_if
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
    std::cout << minivm::run(R"V7SRC(let flag = true; if flag { print "yes"; } else { print "no"; } if false { print "bad"; } print "done";)V7SRC");
    return 0;
}
