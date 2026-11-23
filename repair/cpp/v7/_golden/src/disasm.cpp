#include "disasm.h"

#include <cstdio>

namespace minivm {

static const char* const kNames[36] = {
    "?", "PUSH", "STR", "TRUE", "FALSE", "NULLV",
    "ADD", "SUB", "MUL", "DIV", "NEG",
    "EQ", "NEQ", "LT", "LE", "GT", "GE",
    "CONCAT", "LEN", "NOT", "DISTINCT",
    "DUP", "POP", "SWAP", "JMP", "JZ",
    "SET", "GET", "PRINT", "HALT",
    "ARRNEW", "APUSH", "AGET", "SPAWN", "JOIN", "YIELD"
};

const char* op_name(Op op) {
    unsigned v = static_cast<unsigned>(op);
    if (v >= 36) return "?";
    return kNames[v];
}

static std::string pad4(std::size_t n) {
    char buf[16];
    std::snprintf(buf, sizeof(buf), "%04u", static_cast<unsigned>(n));
    return std::string(buf);
}

static bool has_num(Op op) {
    return op == Op::PUSH || op == Op::JMP || op == Op::JZ ||
           op == Op::SET || op == Op::GET || op == Op::SPAWN;
}

static bool has_text(Op op) {
    return op == Op::STR || op == Op::SET || op == Op::GET || op == Op::SPAWN;
}

std::string disassemble(const Bytecode& bc) {
    std::string out;
    out.reserve(bc.code.size() * 24);
    for (std::size_t i = 0; i < bc.code.size(); ++i) {
        const Ins& in = bc.code[i];
        out += pad4(i);
        out += ' ';
        out += op_name(in.op);
        if (has_num(in.op)) {
            out += ' ';
            out += std::to_string(in.num);
        }
        if (has_text(in.op)) {
            out += ' ';
            out += in.text;
        }
        out += '\n';
    }
    return out;
}

}  // namespace minivm
