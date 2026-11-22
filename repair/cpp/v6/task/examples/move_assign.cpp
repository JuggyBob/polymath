// Move assignment transfers the payload and marks the source.
// Compile with: cl /EHsc /nologo /Od /Iinclude src\*.cpp examples\move_assign.cpp
#include <iostream>
#include <utility>

#include "value.h"

int main() {
    minivm::Value a(std::string("hello"));
    minivm::Value b;
    b = std::move(a);
    std::cout << b.repr() << "\n" << a.repr() << "\n";
    return 0;
}
