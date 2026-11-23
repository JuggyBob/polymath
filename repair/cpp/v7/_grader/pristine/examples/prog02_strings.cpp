// Canonical example: prog02_strings
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
    std::cout << minivm::run(R"V7SRC(print "hello"; print "a" + "b" + "c"; print "x" + 7; print len("abcd"); print "line1\nline2"; print "q\"q"; print "back\\slash";)V7SRC");
    return 0;
}
