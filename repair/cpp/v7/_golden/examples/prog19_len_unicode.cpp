// Canonical example: prog19_len_unicode
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
    std::cout << minivm::run(R"V7SRC(print len("é"); print len("abc"); print len("😀");)V7SRC");
    return 0;
}
