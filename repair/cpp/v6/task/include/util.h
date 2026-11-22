#ifndef MINIVM_UTIL_H
#define MINIVM_UTIL_H

#include <cstddef>
#include <cstdint>
#include <string>

namespace minivm {

int64_t add_sat(int64_t a, int64_t b);
int64_t sub_sat(int64_t a, int64_t b);
int64_t mul_sat(int64_t a, int64_t b);
std::size_t align_up(std::size_t n, std::size_t a);
std::string trim(const std::string& s);
int64_t to_int(const std::string& s);

}  // namespace minivm

#endif
