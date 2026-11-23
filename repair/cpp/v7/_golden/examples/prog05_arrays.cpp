// Canonical example: prog05_arrays
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
    std::cout << minivm::run(R"V7SRC(let a = [1, 3]; print a; print a[0]; print a[2]; print len(a); push a, 9; print a;)V7SRC");
    return 0;
}
