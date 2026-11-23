// Canonical example: prog32_snapshot_badmagic
#include <iostream>
#include <vector>
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
    std::vector<unsigned char> b(36, 0);
    b[0] = 'X'; b[1] = 'X'; b[2] = 'X'; b[3] = 'X';
    try {
        minivm::restore(b);
    } catch (const minivm::MiniVMError& err) {
        std::cout << std::string(err.what()) << std::endl;
    }
    return 0;
}
