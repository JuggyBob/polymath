#ifndef MINIVM_UTIL_H
#define MINIVM_UTIL_H

#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>

namespace minivm {

int64_t add_sat(int64_t a, int64_t b);
int64_t sub_sat(int64_t a, int64_t b);
int64_t mul_sat(int64_t a, int64_t b);
std::string trim(const std::string& s);
int64_t to_int(const std::string& s);
std::string hex_encode(const std::string& s);
std::string hex_decode(const std::string& s);
uint32_t fnv1a(const uint8_t* data, std::size_t n);

}  // namespace minivm

#endif
