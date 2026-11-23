#ifndef MINIVM_BYTECODE_H
#define MINIVM_BYTECODE_H

#include <cstdint>
#include <string>
#include <vector>

namespace minivm {

enum class Op : unsigned char {
    PUSH = 1, STR = 2, TRUE = 3, FALSE = 4, NULLV = 5,
    ADD = 6, SUB = 7, MUL = 8, DIV = 9, NEG = 10,
    EQ = 11, NEQ = 12, LT = 13, LE = 14, GT = 15, GE = 16,
    CONCAT = 17, LEN = 18, NOT = 19, DISTINCT = 20,
    DUP = 21, POP = 22, SWAP = 23,
    JMP = 24, JZ = 25, SET = 26, GET = 27,
    PRINT = 28, HALT = 29,
    ARRNEW = 30, APUSH = 31, AGET = 32,
    SPAWN = 33, JOIN = 34, YIELD = 35
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
    std::vector<std::string> global_names;
};

}  // namespace minivm

#endif
