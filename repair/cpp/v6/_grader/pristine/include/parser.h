#ifndef MINIVM_PARSER_H
#define MINIVM_PARSER_H

#include <cstdint>
#include <string>
#include <vector>

#include "lexer.h"

namespace minivm {

enum class NK : int {
    PUSH, STR, TRUE, FALSE, NULLV, ADD, SUB, MUL, DIV, MOD,
    EQ, NEQ, LT, LE, GT, GE, CONCAT, LEN, NOT, AND, OR,
    DUP, POP, SWAP, JMP, JZ, JNZ, SET, GET, PRINT, HALT,
    ARRNEW, APUSH, AGET, DISTINCT, LABEL, INVALID
};

struct Node {
    NK kind;
    std::string arg;
    int64_t num;
    int line;

    Node() : kind(NK::INVALID), arg(), num(0), line(0) {}
};

std::vector<Node> parse(const std::vector<Token>& toks);

}  // namespace minivm

#endif
