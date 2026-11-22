// A fresh run does not see variables set by an earlier run.
// Compile with: cl /EHsc /nologo /Od /Iinclude src\*.cpp examples\variables_isolated.cpp
#include <iostream>

#include "vm.h"

int main() {
    minivm::run("push 5\nset alpha\nhalt\n");
    std::cout << minivm::run("get alpha\nprint\nhalt\n");
    return 0;
}
