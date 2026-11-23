#ifndef MINIVM_PARSER_H
#define MINIVM_PARSER_H

#include <cstdint>
#include <string>
#include <vector>

#include "lexer.h"

namespace minivm {

enum class NK : int {
    Program, Print, Let, Set, PushStmt, If, While, FiberDecl,
    SpawnStmt, JoinStmt, YieldStmt, ExprStmt,
    IntLit, StrLit, BoolLit, NullLit, Var,
    UnaryNeg, UnaryNot, Binary, Index, ArrayLit,
    Len, Distinct, SpawnExpr
};

struct Node {
    NK kind;
    std::string text;
    int64_t num;
    int line;
    std::vector<Node> kids;

    Node() : kind(NK::Program), text(), num(0), line(0) {}
};

Node parse(const std::vector<Token>& toks);

}  // namespace minivm

#endif
