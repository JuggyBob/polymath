// Canonical example: prog39_snapshot_badversion
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
    std::vector<unsigned char> b(36, 0);
    b[0] = 'M'; b[1] = 'V'; b[2] = '7'; b[3] = 9;
    try {
        minivm::restore(b);
    } catch (const minivm::MiniVMError& err) {
        std::cout << std::string(err.what()) << std::endl;
    }
    return 0;
}
