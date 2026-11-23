// Canonical example: prog35_str_cmp_unicode
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
    std::cout << minivm::run(R"V7SRC(print "é" > "z"; print "é" == "é";)V7SRC");
    return 0;
}
