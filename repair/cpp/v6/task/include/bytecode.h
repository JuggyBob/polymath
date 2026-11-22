#ifndef MINIVM_BYTECODE_H
#define MINIVM_BYTECODE_H

#include <cstdint>
#include <string>
#include <vector>

namespace minivm {

// Opcode numbering is part of the interchange format: the disassembler and
// the serialiser both key off these values.
enum class Op : unsigned char {
    PUSH = 1, STR = 2, TRUE = 3, FALSE = 4, NULLV = 5,
    ADD = 6, SUB = 7, MUL = 8, DIV = 9, MOD = 10,
    EQ = 11, NEQ = 12, LT = 13, LE = 14, GT = 15, GE = 16,
    CONCAT = 17, LEN = 18, NOT = 19, AND = 20, OR = 21,
    DUP = 22, POP = 23, SWAP = 24,
    JMP = 25, JZ = 26, JNZ = 27,
    SET = 28, GET = 29, PRINT = 30, HALT = 31,
    ARRNEW = 32, APUSH = 33, AGET = 34,
    DISTINCT = 35
};

struct Ins {
    Op op;
    int64_t num;
    std::string text;
    int line;

    Ins() : op(Op::HALT), num(0), text(), line(0) {}
};

struct Bytecode {
    std::vector<Ins> code;
    std::vector<std::string> labels;
};

}  // namespace minivm

#endif
