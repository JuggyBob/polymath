#ifndef MINIVM_VM_H
#define MINIVM_VM_H

#include <cstdint>
#include <string>

#include "bytecode.h"

namespace minivm {

struct VMResult {
    std::string output;
    int64_t steps;
    bool halted;

    VMResult() : output(), steps(0), halted(false) {}
};

VMResult execute(const Bytecode& bc, int64_t max_steps = 200000);
std::string run(const std::string& source);

}  // namespace minivm

#endif
