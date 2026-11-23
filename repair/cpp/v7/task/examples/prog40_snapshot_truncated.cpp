// Canonical example: prog40_snapshot_truncated
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
    std::vector<unsigned char> g = minivm::snapshot(vm);
    g.resize(g.size() - 3);
    try {
        minivm::restore(g);
    } catch (const minivm::MiniVMError& err) {
        std::cout << std::string(err.what()) << std::endl;
    }
    return 0;
}
