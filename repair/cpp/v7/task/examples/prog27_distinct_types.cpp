// Canonical example: prog27_distinct_types
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
    std::cout << minivm::run(R"V7SRC(print distinct(["a", "b"]); print distinct([true, false, true]); print distinct([1, "1"]);)V7SRC");
    return 0;
}
