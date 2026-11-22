#include "disasm.h"

#include <cstdio>

namespace minivm {

static const char* const kNames[36] = {
    "?",        // 0
    "push",     // 1  PUSH
    "str",      // 2  STR
    "true",     // 3  TRUE
    "false",    // 4  FALSE
    "null",     // 5  NULLV
    "add",      // 6
    "sub",      // 7
    "mul",      // 8
    "div",      // 9
    "mod",      // 10
    "eq",       // 11
    "neq",      // 12
    "lt",       // 13
    "le",       // 14
    "gt",       // 15
    "ge",       // 16
    "concat",   // 17
    "len",      // 18
    "not",      // 19
    "and",      // 20
    "or",       // 21
    "dup",      // 22
    "pop",      // 23
    "swap",     // 24
    "jmp",      // 25
    "jz",       // 26
    "jnz",      // 27
    "set",      // 28
    "get",      // 29
    "print",    // 30
    "halt",     // 31
    "arrnew",   // 32
    "apush",    // 33
    "aget",     // 34
    "distinct"  // 35
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

std::string disassemble(const Bytecode& bc) {
    std::string out;
    for (std::size_t i = 0; i < bc.code.size(); ++i) {
        const Ins& in = bc.code[i];
        out += pad4(i);
        out += ' ';
        out += op_name(in.op);
        switch (in.op) {
            case Op::PUSH:
            case Op::JMP:
            case Op::JZ:
            case Op::JNZ:
                out += ' ';
                out += std::to_string(in.num);
                break;
            case Op::STR:
            case Op::SET:
            case Op::GET:
                out += ' ';
                out += in.text;
                break;
            default:
                break;
        }
        out += '\n';
    }
    return out;
}

}  // namespace minivm
