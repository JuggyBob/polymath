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
    const uint64_t limit = neg ? (uint64_t(1) << 63) : static_cast<uint64_t>(hi);
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

std::string hex_encode(const std::string& s) {
    static const char* digits = "0123456789abcdef";
    if (s.empty()) return "-";
    std::string out;
    out.reserve(s.size() * 2);
    for (std::size_t i = 0; i < s.size(); ++i) {
        unsigned char c = static_cast<unsigned char>(s[i]);
        out += digits[c >> 4];
        out += digits[c & 15];
    }
    return out;
}

std::string hex_decode(const std::string& s) {
    if (s == "-") return std::string();
    std::string out;
    for (std::size_t i = 0; i + 1 < s.size(); i += 2) {
        int hi = -1, lo = -1;
        if (s[i] >= '0' && s[i] <= '9') hi = s[i] - '0';
        else if (s[i] >= 'a' && s[i] <= 'f') hi = s[i] - 'a' + 10;
        else if (s[i] >= 'A' && s[i] <= 'F') hi = s[i] - 'A' + 10;
        if (s[i + 1] >= '0' && s[i + 1] <= '9') lo = s[i + 1] - '0';
        else if (s[i + 1] >= 'a' && s[i + 1] <= 'f') lo = s[i + 1] - 'a' + 10;
        else if (s[i + 1] >= 'A' && s[i + 1] <= 'F') lo = s[i + 1] - 'A' + 10;
        if (hi < 0 || lo < 0) return std::string();
        out += static_cast<char>((hi << 4) | lo);
    }
    return out;
}

uint32_t fnv1a(const uint8_t* data, std::size_t n) {
    uint32_t h = 2166136261u;
    for (std::size_t i = 0; i < n; ++i) {
        h ^= static_cast<uint32_t>(data[i]);
        h *= 16777619u;
    }
    return h;
}

}  // namespace minivm
