#include "lexer.h"

#include <cctype>

#include "util.h"

namespace minivm {

static std::string lower(const std::string& s) {
    std::string r(s);
    for (std::size_t i = 0; i < r.size(); ++i)
        r[i] = static_cast<char>(std::tolower(static_cast<unsigned char>(r[i])));
    return r;
}

std::vector<Token> lex(const std::string& src) {
    std::vector<Token> out;
    std::size_t pos = 0;
    int line = 1;
    while (pos <= src.size()) {
        std::size_t eol = src.find('\n', pos);
        if (eol == std::string::npos) eol = src.size();
        std::string raw = src.substr(pos, eol - pos);

        bool escaped = false;
        std::size_t cut = raw.size();
        for (std::size_t i = 0; i < raw.size(); ++i) {
            char c = raw[i];
            if (escaped) { escaped = false; continue; }
            if (c == '\\') { escaped = true; continue; }
            if (c == '#') { cut = i; break; }
        }
        raw = raw.substr(0, cut);

        std::size_t i = 0;
        while (i < raw.size()) {
            while (i < raw.size() && (raw[i] == ' ' || raw[i] == '\t' || raw[i] == '\r')) ++i;
            if (i >= raw.size()) break;

            if (raw[i] == '"') {
                ++i;
                std::string val;
                while (i < raw.size() && raw[i] != '"') {
                    char c = raw[i++];
                    if (c == '\\' && i < raw.size()) {
                        char n = raw[i++];
                        if (n == 't') val += '\t';
                        else if (n == 'r') val += '\r';
                        else if (n == '0') val += '\0';
                        else if (n == 'n') { val += '\\'; val += 'n'; }
                        else val += n;
                    } else {
                        val += c;
                    }
                }
                if (i < raw.size()) ++i;
                Token t;
                t.kind = Tok::String;
                t.text = val;
                t.line = line;
                out.push_back(t);
                continue;
            }

            std::size_t start = i;
            while (i < raw.size() && raw[i] != ' ' && raw[i] != '\t' && raw[i] != '\r') ++i;
            std::string w = raw.substr(start, i - start);
            if (w.empty()) continue;

            if (w.size() >= 1 && w[w.size() - 1] == ':') {
                Token t;
                t.kind = Tok::Label;
                t.text = w.substr(0, w.size() - 1);
                t.line = line;
                out.push_back(t);
                continue;
            }
            bool numeric = false;
            if (!w.empty()) {
                std::size_t k = (w[0] == '-' || w[0] == '+') ? 1 : 0;
                numeric = k < w.size();
                for (; k < w.size(); ++k)
                    if (!std::isdigit(static_cast<unsigned char>(w[k]))) { numeric = false; break; }
            }
            Token t;
            t.line = line;
            if (numeric) {
                t.kind = Tok::Number;
                t.text = w;
                t.num = to_int(w);
            } else {
                t.kind = Tok::Word;
                t.text = lower(w);
            }
            out.push_back(t);
        }

        if (eol == src.size()) break;
        pos = eol + 1;
        ++line;
    }
    Token end;
    end.kind = Tok::End;
    end.line = line;
    out.push_back(end);
    return out;
}

}  // namespace minivm
