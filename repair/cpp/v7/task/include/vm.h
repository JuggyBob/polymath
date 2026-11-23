#ifndef MINIVM_VM_H
#define MINIVM_VM_H

#include <cstdint>
#include <string>
#include <utility>
#include <vector>

#include "bytecode.h"
#include "value.h"

namespace minivm {

struct VMResult {
    std::string output;
    int64_t steps;
    bool halted;

    VMResult() : output(), steps(0), halted(false) {}
};

struct Fiber {
    uint32_t id;
    int64_t pc;
    std::vector<Value> stack;
    bool halted;

    Fiber() : id(0), pc(0), stack(), halted(false) {}
};

class MiniVM {
public:
    Bytecode code;
    std::vector<std::string> global_names;
    std::vector<Value> globals;
    std::vector<Fiber> fibers;
    std::vector<uint32_t> ready;
    std::vector<std::pair<uint32_t, uint32_t> > blocked;
    uint32_t next_id;
    std::string output;
    int64_t steps;

    MiniVM() : next_id(1), steps(0) {}

    static MiniVM from_source(const std::string& src);
    std::string run();
    VMResult run_result(int64_t max_steps = 10000000);
};

VMResult execute(const Bytecode& bc, int64_t max_steps = 10000000);
Bytecode compile_source(const std::string& src);
std::string run(const std::string& source);

}  // namespace minivm

#endif
