// Already-aligned sizes stay unchanged.
// Compile with: cl /EHsc /nologo /Od /Iinclude src\*.cpp examples\align_exact.cpp
#include <iostream>

#include "util.h"

int main() {
    std::cout << minivm::align_up(8, 8) << "\n"
              << minivm::align_up(16, 8) << "\n";
    return 0;
}
