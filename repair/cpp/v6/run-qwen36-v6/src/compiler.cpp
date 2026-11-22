#include "compiler.h"

#include <cctype>
#include <map>

namespace minivm {

Op kind_to_op(NK k) {
    switch (k) {
        case NK::PUSH: return Op::PUSH;
        case NK::STR: return Op::STR;
        case NK::TRUE: return Op::TRUE;
        case NK::FALSE: return Op::FALSE;
        case NK::NULLV: return Op::NULLV;
        case NK::ADD: return Op::ADD;
        case NK::SUB: return Op::SUB;
        case NK::MUL: return Op::MUL;
        case NK::DIV: return Op::DIV;
        case NK::MOD: return Op::MOD;
        case NK::EQ: return Op::EQ;
        case NK::NEQ: return Op::NEQ;
        case NK::LT: return Op::LT;
        case NK::LE: return Op::LE;
        case NK::GT: return Op::GT;
        case NK::GE: return Op::GE;
        case NK::CONCAT: return Op::CONCAT;
        case NK::LEN: return Op::LEN;
        case NK::NOT: return Op::NOT;
        case NK::AND: return Op::AND;
        case NK::OR: return Op::OR;
        case NK::DUP: return Op::DUP;
        case NK::POP: return Op::POP;
        case NK::SWAP: return Op::SWAP;
        case NK::JMP: return Op::JMP;
        case NK::JZ: return Op::JZ;
        case NK::JNZ: return Op::JNZ;
        case NK::SET: return Op::SET;
        case NK::GET: return Op::GET;
        case NK::PRINT: return Op::PRINT;
        case NK::HALT: return Op::HALT;
        case NK::ARRNEW: return Op::ARRNEW;
        case NK::APUSH: return Op::APUSH;
        case NK::AGET: return Op::AGET;
        case NK::DISTINCT: return Op::DISTINCT;
        default: return Op::HALT;
    }
}

Bytecode compile(const std::vector<Node>& nodes) {
    std::map<std::string, int64_t> labels;
    std::size_t count = 0;
    for (std::size_t i = 0; i < nodes.size(); ++i) {
        if (nodes[i].kind == NK::LABEL) labels[nodes[i].arg] = static_cast<int64_t>(count);
        else ++count;
    }

    auto find_label = [&](const std::string& name) -> int64_t {
        for (const auto& p : labels) {
            std::string lo_name = p.first;
            std::string lo_arg = name;
            if (lo_name.size() == lo_arg.size()) {
                bool match = true;
                for (std::size_t k = 0; k < lo_name.size(); ++k) {
                    if (std::tolower(static_cast<unsigned char>(lo_name[k])) !=
                        std::tolower(static_cast<unsigned char>(lo_arg[k]))) {
                        match = false;
                        break;
                    }
                }
                if (match) return p.second;
            }
        }
        return 0;
    };

    Bytecode bc;
    bc.code.reserve(count);
    for (std::size_t i = 0; i < nodes.size(); ++i) {
        const Node& n = nodes[i];
        if (n.kind == NK::LABEL) {
            bc.labels.push_back(n.arg);
            continue;
        }
        Ins in;
        in.op = kind_to_op(n.kind);
        in.line = n.line;
        if (n.kind == NK::PUSH) in.num = n.num;
        else if (n.kind == NK::STR) in.text = n.arg;
        else if (n.kind == NK::JMP || n.kind == NK::JZ || n.kind == NK::JNZ) {
            in.text = n.arg;
            in.num = find_label(n.arg);
        } else if (n.kind == NK::SET || n.kind == NK::GET) {
            in.text = n.arg;
        }
        bc.code.push_back(in);
    }
    return bc;
}

}  // namespace minivm
