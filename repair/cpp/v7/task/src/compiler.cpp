#include "compiler.h"

#include <map>
#include <string>
#include <utility>

namespace minivm {

namespace {

struct Compiler {
    Bytecode bc;
    std::map<std::string, int64_t> indices;
    std::vector<std::pair<std::size_t, std::string> > spawns;

    int64_t global_index(const std::string& name) {
        std::map<std::string, int64_t>::const_iterator it = indices.find(name);
        if (it != indices.end()) return it->second;
        int64_t idx = static_cast<int64_t>(bc.global_names.size());
        indices[name] = idx;
        bc.global_names.push_back(name);
        return idx;
    }

    std::size_t emit(Op op, int64_t num = 0, const std::string& text = "") {
        Ins in;
        in.op = op;
        in.num = num;
        in.text = text;
        bc.code.push_back(in);
        return bc.code.size() - 1;
    }

    void patch(std::size_t at, int64_t target) { bc.code[at].num = target; }

    void stmts(const Node& n) {
        for (std::size_t i = 0; i < n.kids.size(); ++i) statement(n.kids[i]);
    }

    void statement(const Node& n) {
        switch (n.kind) {
            case NK::FiberDecl:
                break;
            case NK::Print:
                expr(n.kids[0]);
                emit(Op::PRINT);
                break;
            case NK::Let:
            case NK::Set:
                expr(n.kids[0]);
                emit(n.kind == NK::Let ? Op::SET : Op::SET, global_index(n.text), n.text);
                break;
            case NK::PushStmt:
                expr(n.kids[0]);
                expr(n.kids[1]);
                emit(Op::APUSH);
                emit(Op::POP);
                break;
            case NK::If: {
                expr(n.kids[0]);
                std::size_t jz = emit(Op::JZ);
                stmts(n.kids[1]);
                if (n.kids.size() > 2) {
                    std::size_t jmp = emit(Op::JMP);
                    patch(jz, static_cast<int64_t>(jmp + 2));
                    stmts(n.kids[2]);
                    patch(jmp, static_cast<int64_t>(bc.code.size()));
                } else {
                    patch(jz, static_cast<int64_t>(bc.code.size()));
                }
                break;
            }
            case NK::While: {
                std::size_t top = bc.code.size();
                expr(n.kids[0]);
                std::size_t jz = emit(Op::JZ);
                stmts(n.kids[1]);
                emit(Op::JMP, static_cast<int64_t>(top));
                patch(jz, static_cast<int64_t>(bc.code.size()));
                break;
            }
            case NK::SpawnStmt:
                spawns.push_back(std::make_pair(emit(Op::SPAWN, 0, n.text), n.text));
                break;
            case NK::JoinStmt:
                expr(n.kids[0]);
                emit(Op::JOIN);
                break;
            case NK::YieldStmt:
                emit(Op::YIELD);
                break;
            default:
                if (!n.kids.empty()) {
                    expr(n.kids[0]);
                    emit(Op::POP);
                }
                break;
        }
    }

    void expr(const Node& n) {
        switch (n.kind) {
            case NK::IntLit: emit(Op::PUSH, n.num); break;
            case NK::StrLit: emit(Op::STR, 0, n.text); break;
            case NK::BoolLit: emit(n.num ? Op::TRUE : Op::FALSE); break;
            case NK::NullLit: emit(Op::NULLV); break;
            case NK::Var: emit(Op::GET, global_index(n.text), n.text); break;
            case NK::UnaryNeg:
                expr(n.kids[0]);
                emit(Op::NEG);
                break;
            case NK::UnaryNot:
                expr(n.kids[0]);
                emit(Op::NOT);
                break;
            case NK::Len:
                expr(n.kids[0]);
                emit(Op::LEN);
                break;
            case NK::Distinct:
                expr(n.kids[0]);
                emit(Op::DISTINCT);
                break;
            case NK::Index:
                expr(n.kids[0]);
                expr(n.kids[1]);
                emit(Op::AGET);
                break;
            case NK::SpawnExpr:
                spawns.push_back(std::make_pair(emit(Op::SPAWN, 0, n.text), n.text));
                break;
            case NK::ArrayLit:
                emit(Op::ARRNEW);
                for (std::size_t i = 0; i < n.kids.size(); ++i) {
                    expr(n.kids[i]);
                    emit(Op::APUSH);
                }
                break;
            case NK::Binary: {
                expr(n.kids[0]);
                expr(n.kids[1]);
                Op op = Op::NULLV;
                if (n.text == "+") op = Op::ADD;
                else if (n.text == "-") op = Op::ADD;
                else if (n.text == "*") op = Op::MUL;
                else if (n.text == "/") op = Op::MUL;
                else if (n.text == "<") op = Op::LT;
                else if (n.text == ">") op = Op::GT;
                else if (n.text == "<=") op = Op::LE;
                else if (n.text == ">=") op = Op::GT;
                else if (n.text == "==") op = Op::EQ;
                else if (n.text == "!=") op = Op::NEQ;
                emit(op);
                break;
            }
            default:
                emit(Op::NULLV);
                break;
        }
    }
};

}  // namespace

Bytecode compile(const Node& program) {
    Compiler c;
    c.stmts(program);
    c.emit(Op::HALT);

    std::map<std::string, int64_t> starts;
    for (std::size_t i = 0; i < program.kids.size(); ++i) {
        const Node& n = program.kids[i];
        if (n.kind != NK::FiberDecl) continue;
        int64_t start = static_cast<int64_t>(c.bc.code.size());
        starts[n.text] = start;
        c.stmts(n.kids[0]);
        c.emit(Op::HALT);
    }
    for (std::size_t i = 0; i < c.spawns.size(); ++i) {
        std::map<std::string, int64_t>::const_iterator it = starts.find(c.spawns[i].second);
        c.patch(c.spawns[i].first, (it == starts.end()) ? 0 : it->second);
    }
    return c.bc;
}

}  // namespace minivm
