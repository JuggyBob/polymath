#include "lexer.h"

#include <cctype>

#include "util.h"

namespace minivm {

static const struct Keyword { const char* word; Tok kind; } kKeywords[] = {
    {"print", Tok::KwPrint}, {"let", Tok::KwLet}, {"set", Tok::KwSet},
    {"push", Tok::KwPush},   {"if", Tok::KwIf},   {"else", Tok::KwElse},
    {"while", Tok::KwWhile}, {"fiber", Tok::KwFiber}, {"spawn", Tok::KwSpawn},
    {"join", Tok::KwJoin},   {"yield", Tok::KwYield},
    {"true", Tok::True},     {"false", Tok::False}, {"null", Tok::Null}
};

static Tok keyword_of(const std::string& w) {
    for (std::size_t i = 0; i < sizeof(kKeywords) / sizeof(kKeywords[0]); ++i)
        if (w == kKeywords[i].word) return kKeywords[i].kind;
    return Tok::Ident;
}

static void push_tok(std::vector<Token>& out, Tok k, const std::string& text,
                     int64_t num, int line) {
    Token t;
    t.kind = k;
    t.text = text;
    t.num = num;
    t.line = line;
    out.push_back(t);
}

std::vector<Token> lex(const std::string& src) {
    std::vector<Token> out;
    std::size_t i = 0;
    int line = 1;
    while (i < src.size()) {
        char c = src[i];
        if (c == '\n') { ++i; ++line; continue; }
        if (c == ' ' || c == '\t' || c == '\r') { ++i; continue; }
        if (c == '#') {
            while (i < src.size() && src[i] != '\n') ++i;
            continue;
        }
        if (c == '"') {
            ++i;
            std::string val;
            while (i < src.size() && src[i] != '"') {
                char ch = src[i++];
                if (ch == '\\' && i < src.size()) {
                    char n = src[i++];
                    if (n == 'n') val += '\n';
                    else if (n == 't') val += '\t';
                    else if (n == '0') val += '\0';
                    else if (n == '\\') val += '\\';
                    else if (n == '"') val += '"';
                    else val += n;
                } else {
                    val += ch;
                }
            }
            if (i < src.size()) ++i;
            push_tok(out, Tok::Str, val, 0, line);
            continue;
        }
        if (c >= '0' && c <= '9') {
            std::size_t start = i;
            while (i < src.size() && src[i] >= '0' && src[i] <= '9') ++i;
            std::string w = src.substr(start, i - start);
            push_tok(out, Tok::Int, w, to_int(w), line);
            continue;
        }
        if (std::isalpha(static_cast<unsigned char>(c)) || c == '_') {
            std::size_t start = i;
            while (i < src.size() &&
                   (std::isalnum(static_cast<unsigned char>(src[i])) || src[i] == '_')) ++i;
            std::string w = src.substr(start, i - start);
            push_tok(out, keyword_of(w), w, 0, line);
            continue;
        }
        if (c == '>' && i + 1 < src.size() && src[i + 1] == '=') {
            i += 2; push_tok(out, Tok::Ge, ">=", 0, line); continue;
        }
        if (c == '<' && i + 1 < src.size() && src[i + 1] == '=') {
            i += 2; push_tok(out, Tok::Le, "<=", 0, line); continue;
        }
        if (c == '=' && i + 1 < src.size() && src[i + 1] == '=') {
            i += 2; push_tok(out, Tok::EqEq, "==", 0, line); continue;
        }
        if (c == '!' && i + 1 < src.size() && src[i + 1] == '=') {
            i += 2; push_tok(out, Tok::Ne, "!=", 0, line); continue;
        }
        ++i;
        switch (c) {
            case '+': push_tok(out, Tok::Plus, "+", 0, line); break;
            case '-': push_tok(out, Tok::Minus, "-", 0, line); break;
            case '*': push_tok(out, Tok::Star, "*", 0, line); break;
            case '/': push_tok(out, Tok::Slash, "/", 0, line); break;
            case '<': push_tok(out, Tok::Lt, "<", 0, line); break;
            case '>': push_tok(out, Tok::Gt, ">", 0, line); break;
            case '!': push_tok(out, Tok::Bang, "!", 0, line); break;
            case '=': push_tok(out, Tok::Assign, "=", 0, line); break;
            case '(': push_tok(out, Tok::LParen, "(", 0, line); break;
            case ')': push_tok(out, Tok::RParen, ")", 0, line); break;
            case '{': push_tok(out, Tok::LBrace, "{", 0, line); break;
            case '}': push_tok(out, Tok::RBrace, "}", 0, line); break;
            case '[': push_tok(out, Tok::LBracket, "[", 0, line); break;
            case ']': push_tok(out, Tok::RBracket, "]", 0, line); break;
            case ',': push_tok(out, Tok::Comma, ",", 0, line); break;
            case ';': push_tok(out, Tok::Semi, ";", 0, line); break;
            default: break;
        }
    }
    push_tok(out, Tok::End, "", 0, line);
    return out;
}

}  // namespace minivm
