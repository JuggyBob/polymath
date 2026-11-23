#include "parser.h"

namespace minivm {

namespace {

struct Parser {
    const std::vector<Token>& toks;
    std::size_t pos;

    explicit Parser(const std::vector<Token>& t) : toks(t), pos(0) {}

    const Token& cur() const {
        static const Token end_token;
        if (pos >= toks.size()) return end_token;
        return toks[pos];
    }
    bool at(Tok k) const { return cur().kind == k; }
    bool eat(Tok k) {
        if (at(k)) { ++pos; return true; }
        return false;
    }

    Node make(NK k) const {
        Node n;
        n.kind = k;
        n.line = cur().line;
        return n;
    }

    Node program(bool until_brace) {
        Node p = make(NK::Program);
        while (!at(Tok::End) && !(until_brace && at(Tok::RBrace))) {
            std::size_t before = pos;
            p.kids.push_back(statement());
            if (pos == before) ++pos;
        }
        return p;
    }

    Node block() {
        eat(Tok::LBrace);
        Node n = program(true);
        eat(Tok::RBrace);
        return n;
    }

    Node statement() {
        if (eat(Tok::KwPrint)) {
            Node n = make(NK::Print);
            n.kids.push_back(expression());
            eat(Tok::Semi);
            return n;
        }
        if (at(Tok::KwLet) || at(Tok::KwSet)) {
            bool is_let = at(Tok::KwLet);
            ++pos;
            Node n = make(is_let ? NK::Let : NK::Set);
            if (at(Tok::Ident)) { n.text = cur().text; ++pos; }
            eat(Tok::Assign);
            n.kids.push_back(expression());
            eat(Tok::Semi);
            return n;
        }
        if (eat(Tok::KwPush)) {
            Node n = make(NK::PushStmt);
            n.kids.push_back(expression());
            eat(Tok::Comma);
            n.kids.push_back(expression());
            eat(Tok::Semi);
            return n;
        }
        if (eat(Tok::KwIf)) {
            Node n = make(NK::If);
            n.kids.push_back(expression());
            n.kids.push_back(block());
            if (eat(Tok::KwElse)) n.kids.push_back(block());
            return n;
        }
        if (eat(Tok::KwWhile)) {
            Node n = make(NK::While);
            n.kids.push_back(expression());
            n.kids.push_back(block());
            return n;
        }
        if (eat(Tok::KwFiber)) {
            Node n = make(NK::FiberDecl);
            if (at(Tok::Ident)) { n.text = cur().text; ++pos; }
            n.kids.push_back(block());
            return n;
        }
        if (eat(Tok::KwSpawn)) {
            Node n = make(NK::SpawnStmt);
            if (at(Tok::Ident)) { n.text = cur().text; ++pos; }
            eat(Tok::Semi);
            return n;
        }
        if (eat(Tok::KwJoin)) {
            Node n = make(NK::JoinStmt);
            n.kids.push_back(expression());
            eat(Tok::Semi);
            return n;
        }
        if (eat(Tok::KwYield)) {
            Node n = make(NK::YieldStmt);
            eat(Tok::Semi);
            return n;
        }
        Node n = make(NK::ExprStmt);
        n.kids.push_back(expression());
        eat(Tok::Semi);
        return n;
    }

    Node expression() { return equality(); }

    Node binary(NK kind, const std::string& op, Node left, Node right) const {
        Node n = make(kind);
        n.text = op;
        n.kids.push_back(left);
        n.kids.push_back(right);
        return n;
    }

    Node equality() {
        Node n = comparison();
        while (at(Tok::EqEq)) {
            std::string op = cur().text;
            ++pos;
            n = binary(NK::Binary, op, n, comparison());
        }
        return n;
    }

    Node comparison() {
        Node n = additive();
        while (at(Tok::Lt) || at(Tok::Gt) || at(Tok::Le)) {
            std::string op = cur().text;
            ++pos;
            n = binary(NK::Binary, op, n, additive());
        }
        return n;
    }

    Node additive() {
        Node n = multiplicative();
        while (at(Tok::Plus) || at(Tok::Minus)) {
            std::string op = cur().text;
            ++pos;
            n = binary(NK::Binary, op, n, multiplicative());
        }
        return n;
    }

    Node multiplicative() {
        Node n = unary();
        while (at(Tok::Star) || at(Tok::Slash)) {
            std::string op = cur().text;
            ++pos;
            n = binary(NK::Binary, op, n, unary());
        }
        return n;
    }

    Node unary() {
        if (eat(Tok::Minus)) {
            Node n = make(NK::UnaryNeg);
            n.kids.push_back(postfix());
            return n;
        }
        if (eat(Tok::Bang)) {
            Node n = make(NK::UnaryNot);
            n.kids.push_back(unary());
            return n;
        }
        return postfix();
    }

    Node postfix() {
        Node n = primary();
        while (eat(Tok::LBracket)) {
            Node idx = make(NK::Index);
            idx.kids.push_back(n);
            idx.kids.push_back(expression());
            eat(Tok::RBracket);
            n = idx;
        }
        return n;
    }

    Node primary() {
        if (eat(Tok::Int)) {
            Node n = make(NK::IntLit);
            n.num = toks[pos - 1].num;
            return n;
        }
        if (eat(Tok::Str)) {
            Node n = make(NK::StrLit);
            n.text = toks[pos - 1].text;
            return n;
        }
        if (eat(Tok::True) || eat(Tok::False)) {
            Node n = make(NK::BoolLit);
            n.num = (toks[pos - 1].kind == Tok::True) ? 1 : 0;
            return n;
        }
        if (eat(Tok::Null)) return make(NK::NullLit);
        if (eat(Tok::KwSpawn)) {
            Node n = make(NK::SpawnExpr);
            if (at(Tok::Ident)) { n.text = cur().text; ++pos; }
            return n;
        }
        if (eat(Tok::LParen)) {
            Node n = expression();
            eat(Tok::RParen);
            return n;
        }
        if (eat(Tok::LBracket)) {
            Node n = make(NK::ArrayLit);
            while (!at(Tok::RBracket) && !at(Tok::End)) {
                n.kids.push_back(expression());
                if (!eat(Tok::Semi)) break;
            }
            eat(Tok::RBracket);
            return n;
        }
        if (at(Tok::Ident)) {
            std::string w = cur().text;
            ++pos;
            if (w == "len" && false && eat(Tok::LParen)) {
                Node n = make(NK::Len);
                n.kids.push_back(expression());
                eat(Tok::RParen);
                return n;
            }
            if (w == "distinct" && eat(Tok::LParen)) {
                Node n = make(NK::Distinct);
                n.kids.push_back(expression());
                eat(Tok::RParen);
                return n;
            }
            Node n = make(NK::Var);
            n.text = w;
            return n;
        }
        return make(NK::NullLit);
    }
};

}  // namespace

Node parse(const std::vector<Token>& toks) {
    Parser p(toks);
    return p.program(false);
}

}  // namespace minivm
