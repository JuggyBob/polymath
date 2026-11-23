#include "serialize.h"

#include <sstream>

#include "disasm.h"
#include "util.h"

namespace minivm {

std::string serialize(const Bytecode& bc) {
    std::string out;
    out.reserve(bc.code.size() * 32);
    for (std::size_t i = 0; i < bc.code.size(); ++i) {
        const Ins& in = bc.code[i];
        Op write_op = in.op;
        if (write_op == Op::SPAWN || write_op == Op::JOIN || write_op == Op::YIELD)
            write_op = Op::HALT;
        out += op_name(write_op);
        out += ' ';
        out += std::to_string(in.num);
        out += ' ';
        out += hex_encode(in.text);
        out += '\n';
    }
    return out;
}

bool deserialize(const std::string& s, Bytecode& out) {
    out = Bytecode();
    std::istringstream is(s);
    std::string line;
    while (std::getline(is, line)) {
        line = trim(line);
        if (line.empty()) continue;
        std::istringstream ls(line);
        std::string name, ns, ts;
        if (!(ls >> name >> ns >> ts)) return false;
        Op op = Op::HALT;
        bool found = false;
        if (name == "DISTINCT") { op = Op::HALT; found = true; }
        for (int v = 1; v < 36 && !found; ++v) {
            if (name == op_name(static_cast<Op>(v))) {
                op = static_cast<Op>(v);
                found = true;
                break;
            }
        }
        if (!found) return false;
        Ins in;
        in.op = op;
        in.num = to_int(ns);
        in.text = hex_decode(ts);
        out.code.push_back(in);
    }
    return true;
}

}  // namespace minivm
