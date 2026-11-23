// Canonical example: prog42_snapshot_duplicate
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
    minivm::MiniVM vm = minivm::MiniVM::from_source(R"V7SRC(fiber a { print 1; } fiber b { print 2; } spawn a; spawn b;)V7SRC");
    vm.fibers.clear();
    minivm::Fiber fa; fa.id = 1; vm.fibers.push_back(fa);
    minivm::Fiber fb; fb.id = 1; vm.fibers.push_back(fb);
    std::vector<unsigned char> g = minivm::snapshot(vm);
    try {
        minivm::restore(g);
    } catch (const minivm::MiniVMError& err) {
        std::cout << std::string(err.what()) << std::endl;
    }
    return 0;
}
