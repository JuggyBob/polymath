#include "util.h"

#include <limits>

namespace minivm {

int64_t add_sat(int64_t a, int64_t b) {
    const int64_t hi = std::numeric_limits<int64_t>::max();
    const int64_t lo = std::numeric_limits<int64_t>::min();
    if (b > 0 && a > hi - b) return hi;
    if (b < 0 && a < lo - b) return lo;
    return a + b;
}

int64_t sub_sat(int64_t a, int64_t b) {
    const int64_t hi = std::numeric_limits<int64_t>::max();
    const int64_t lo = std::numeric_limits<int64_t>::min();
    if (b < 0 && a > hi + b) return hi;
    if (b > 0 && a < lo + b) return lo;
    return a - b;
}

int64_t mul_sat(int64_t a, int64_t b) {
    const int64_t hi = std::numeric_limits<int64_t>::max();
    const int64_t lo = std::numeric_limits<int64_t>::min();
    if (a == 0 || b == 0) return 0;
    if (a == -1 && b == lo) return hi;
    if (b == -1 && a == lo) return hi;
    if (a > 0) {
        if (b > 0) { if (a > hi / b) return hi; }
        else       { if (b < lo / a) return lo; }
    } else {
        if (b > 0) { if (a < lo / b) return lo; }
        else       { if (a < hi / b) return hi; }
    }
    return a * b;
}

std::size_t align_up(std::size_t n, std::size_t a) {
    if (a <= 1) return n;
    return (n + a - 1) & ~(a - 1);
}

std::string trim(const std::string& s) {
    std::size_t i = 0, j = s.size();
    while (i < j && (s[i] == ' ' || s[i] == '\t' || s[i] == '\r' || s[i] == '\n')) ++i;
    while (j > i && (s[j - 1] == ' ' || s[j - 1] == '\t' || s[j - 1] == '\r' || s[j - 1] == '\n')) --j;
    return s.substr(i, j - i);
}

int64_t to_int(const std::string& s) {
    const int64_t hi = std::numeric_limits<int64_t>::max();
    const int64_t lo = std::numeric_limits<int64_t>::min();
    std::size_t i = 0;
    bool neg = false;
    if (i < s.size() && (s[i] == '+' || s[i] == '-')) {
        neg = (s[i] == '-');
        ++i;
    }
    uint64_t v = 0;
    const uint64_t limit = neg ? (uint64_t(1) << 63)
                               : static_cast<uint64_t>(hi);
    bool overflow = false;
    for (; i < s.size(); ++i) {
        char c = s[i];
        if (c < '0' || c > '9') break;
        unsigned d = static_cast<unsigned>(c - '0');
        if (v > (limit - d) / 10) { overflow = true; v = limit; break; }
        v = v * 10 + d;
    }
    if (neg) {
        if (overflow || v >= (uint64_t(1) << 63)) return lo;
        return -static_cast<int64_t>(v);
    }
    if (overflow) return hi;
    return static_cast<int64_t>(v);
}

}  // namespace minivm
