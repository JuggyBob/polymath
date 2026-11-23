#ifndef MINIVM_SNAPSHOT_H
#define MINIVM_SNAPSHOT_H

#include <cstdint>
#include <exception>
#include <string>
#include <vector>

#include "vm.h"

namespace minivm {

class MiniVMError : public std::exception {
public:
    explicit MiniVMError(std::string code) : code_(std::move(code)) {}
    const char* what() const noexcept override { return code_.c_str(); }

private:
    std::string code_;
};

std::vector<uint8_t> snapshot(const MiniVM& vm);
MiniVM restore(const std::vector<uint8_t>& bytes);

}  // namespace minivm

#endif
