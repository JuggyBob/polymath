#include "serialize.h"

#include <map>
#include <sstream>

#include "disasm.h"
#include "util.h"

namespace minivm {

static std::string hex_encode(const std::string& s) {
    static const char* d = "0123456789abcdef";
    if (s.empty()) return "-";
    std::string out;
    out.reserve(s.size() * 2);
    for (std::size_t i = 0; i < s.size(); ++i) {
        unsigned char c = static_cast<unsigned char>(s[i]);
        out += d[c >> 4];
        out += d[c & 15];
    }
    return out;
}

static std::string hex_decode(const std::string& s) {
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

std::string serialize(const Bytecode& bc) {
    std::string out;
    for (std::size_t i = 0; i < bc.code.size(); ++i) {
        const Ins& in = bc.code[i];
        out += op_name(in.op);
        out += ' ';
        out += std::to_string(in.num);
        out += ' ';
        out += hex_encode(in.text);
        out += '\n';
    }
    return out;
}

bool deserialize(const std::string& s, Bytecode& out) {
    static const char* const names[36] = {
        "?", "push", "str", "true", "false", "null",
        "add", "sub", "mul", "div", "mod",
        "eq", "neq", "lt", "le", "gt", "ge",
        "concat", "len", "not", "and", "or",
        "dup", "pop", "swap", "jmp", "jz", "jnz",
        "set", "get", "print", "halt",
        "arrnew", "apush", "aget", "distinct"
    };
    out = Bytecode();
    std::istringstream is(s);
    std::string line;
    while (std::getline(is, line)) {
        line = trim(line);
        if (line.empty()) continue;
        std::istringstream ls(line);
        std::string name, ns, ts;
        if (!(ls >> name >> ns >> ts)) return false;
        Op op = Op::HALT;
        bool found = false;
        for (int i = 1; i < 36; ++i) {
            if (name == names[i]) { op = static_cast<Op>(i); found = true; break; }
        }
        if (!found) return false;
        Ins in;
        in.op = op;
        in.num = to_int(ns);
        in.text = hex_decode(ts);
        out.code.push_back(in);
    }
    return true;
}

}  // namespace minivm
