// Canonical example: prog38_snapshot_fibers
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
    minivm::MiniVM vm = minivm::MiniVM::from_source(R"V7SRC(fiber a { print 1; yield; print 2; } spawn a; yield;)V7SRC");
    minivm::MiniVM back = minivm::restore(minivm::snapshot(vm));
    std::cout << back.run();
    return 0;
}
