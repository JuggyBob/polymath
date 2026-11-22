#include "parser.h"

namespace minivm {

static NK word_kind(const std::string& w) {
    if (w == "push")    return NK::PUSH;
    if (w == "str")     return NK::STR;
    if (w == "true")    return NK::TRUE;
    if (w == "false")   return NK::FALSE;
    if (w == "null")    return NK::NULLV;
    if (w == "add")     return NK::ADD;
    if (w == "sub")     return NK::SUB;
    if (w == "mul")     return NK::MUL;
    if (w == "div")     return NK::DIV;
    if (w == "mod")     return NK::MOD;
    if (w == "eq")      return NK::EQ;
    if (w == "neq")     return NK::NEQ;
    if (w == "lt")      return NK::LT;
    if (w == "le")      return NK::LE;
    if (w == "gt")      return NK::GT;
    if (w == "ge")      return NK::GE;
    if (w == "concat")  return NK::CONCAT;
    if (w == "len")     return NK::LEN;
    if (w == "not")     return NK::NOT;
    if (w == "and")     return NK::AND;
    if (w == "or")      return NK::OR;
    if (w == "dup")     return NK::DUP;
    if (w == "pop")     return NK::POP;
    if (w == "swap")    return NK::SWAP;
    if (w == "jmp")     return NK::JMP;
    if (w == "jz")      return NK::JZ;
    if (w == "jnz")     return NK::JNZ;
    if (w == "set")     return NK::SET;
    if (w == "get")     return NK::GET;
    if (w == "print")   return NK::PRINT;
    if (w == "halt")    return NK::HALT;
    if (w == "arrnew")  return NK::ARRNEW;
    if (w == "apush")   return NK::APUSH;
    if (w == "aget")    return NK::AGET;
    if (w == "distinct") return NK::DISTINCT;
    return NK::INVALID;
}

std::vector<Node> parse(const std::vector<Token>& toks) {
    std::vector<Node> nodes;
    for (std::size_t i = 0; i < toks.size(); ++i) {
        const Token& t = toks[i];
        Node n;
        n.line = t.line;
        if (t.kind == Tok::End) continue;
        if (t.kind == Tok::Number) {
            n.kind = NK::PUSH;
            n.num = t.num;
        } else if (t.kind == Tok::String) {
            n.kind = NK::STR;
            n.arg = t.text;
        } else if (t.kind == Tok::Label) {
            n.kind = NK::LABEL;
            n.arg = t.text;
        } else if (t.kind == Tok::Distinct) {
            n.kind = NK::DISTINCT;
        } else if (t.kind == Tok::Word) {
            NK k = word_kind(t.text);
            n.kind = k;
            if (k == NK::PUSH) {
                if (i + 1 < toks.size() && toks[i + 1].kind == Tok::Number) {
                    n.num = toks[i + 1].num;
                    ++i;
                }
            } else if (k == NK::STR) {
                if (i + 1 < toks.size() && toks[i + 1].kind == Tok::String) {
                    n.arg = toks[i + 1].text;
                    ++i;
                }
            } else if (k == NK::JMP || k == NK::JZ || k == NK::JNZ ||
                       k == NK::SET || k == NK::GET) {
                if (i + 1 < toks.size() &&
                    (toks[i + 1].kind == Tok::Word || toks[i + 1].kind == Tok::Label)) {
                    n.arg = toks[i + 1].text;
                    ++i;
                }
            }
        }
        nodes.push_back(n);
    }
    return nodes;
}

}  // namespace minivm
