#ifndef MINIVM_LEXER_H
#define MINIVM_LEXER_H

#include <cstdint>
#include <string>
#include <vector>

namespace minivm {

enum class Tok : int { End = 0, Number, String, Word, Label, Distinct };

struct Token {
    Tok kind;
    std::string text;
    int64_t num;
    int line;

    Token() : kind(Tok::End), text(), num(0), line(0) {}
};

std::vector<Token> lex(const std::string& src);

}  // namespace minivm

#endif
