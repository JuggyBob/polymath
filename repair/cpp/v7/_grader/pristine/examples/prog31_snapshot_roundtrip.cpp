// Canonical example: prog31_snapshot_roundtrip
#include <iostream>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

#include "snapshot.h"
#include "vm.h"

int main() {
#ifdef _WIN32
    _setmode(_fileno(stdout), _O_BINARY);
#endif
    minivm::MiniVM vm = minivm::MiniVM::from_source(R"V7SRC(let x = 5; print x + 1;)V7SRC");
    minivm::MiniVM vm2 = minivm::restore(minivm::snapshot(vm));
    std::cout << vm2.run();
    return 0;
}
