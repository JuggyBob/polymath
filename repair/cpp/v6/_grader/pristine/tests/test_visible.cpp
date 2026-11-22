#include <cstdint>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

#include "bytecode.h"
#include "compiler.h"
#include "disasm.h"
#include "lexer.h"
#include "parser.h"
#include "serialize.h"
#include "util.h"
#include "value.h"
#include "vm.h"

#define CHECK(name, cond) \
    std::cout << "TEST " << #name << " " << ((cond) ? "PASS" : "FAIL") << "\n"

using namespace minivm;

int main() {
    std::cout << std::unitbuf;

    // ---- numeric helpers: ordinary inputs ----
    CHECK(util_add_small, add_sat(5, 7) == 12);
    CHECK(util_sub_small, sub_sat(9, 4) == 5);
    CHECK(util_mul_small, mul_sat(6, 7) == 42);
    CHECK(util_align_small, align_up(1, 8) == 8 && align_up(9, 8) == 16);
    CHECK(util_trim, trim("  hi \t\n") == "hi");
    CHECK(util_to_int, to_int("-42") == -42 && to_int("+7") == 7);

    // ---- value representation and truthiness ----
    CHECK(rep_int, Value(int64_t(42)).repr() == "42");
    CHECK(rep_str, Value(std::string("hello")).repr() == "hello");
    CHECK(rep_bool, Value(true).repr() == "true" && Value(false).repr() == "false");
    CHECK(rep_null, Value().repr() == "null");
    Value arr = Value::array_value();
    arr.arr.push_back(Value(int64_t(1)));
    arr.arr.push_back(Value(std::string("x")));
    CHECK(rep_array, arr.repr() == "[1, x]");

    CHECK(truth_int, Value(int64_t(3)).truthy());
    CHECK(truth_str, Value(std::string("x")).truthy() && !Value(std::string("")).truthy());
    CHECK(truth_bool, Value(true).truthy() && !Value(false).truthy());
    CHECK(truth_null, !Value().truthy());
    Value empty = Value::array_value();
    CHECK(truth_array, !empty.truthy() && arr.truthy());

    CHECK(eq_same, value_eq(Value(int64_t(1)), Value(int64_t(1))));
    CHECK(eq_type_strict, !value_eq(Value(int64_t(1)), Value(std::string("1"))));
    CHECK(eq_null, value_eq(Value(), Value()));
    CHECK(eq_array, value_eq(arr, arr));

    Value mv_src(std::string("move-me"));
    Value mv_dst(std::move(mv_src));
    CHECK(value_move_ctor, mv_dst.repr() == "move-me" && mv_src.repr() == "<moved>");

    // ---- pipeline, fully observable ----
    std::vector<Token> toks = lex("push 2\nadd # ignored\nprint\nhalt\n");
    CHECK(lex_kinds, toks.size() == 6 && toks[0].kind == Tok::Word &&
          toks[1].kind == Tok::Number && toks[2].kind == Tok::Word &&
          toks[3].kind == Tok::Word && toks[4].kind == Tok::Word &&
          toks[5].kind == Tok::End);
    std::vector<Node> nodes = parse(toks);
    CHECK(parse_nodes, nodes.size() == 4 && nodes[0].kind == NK::PUSH &&
          nodes[1].kind == NK::ADD && nodes[2].kind == NK::PRINT);
    Bytecode bc = compile(nodes);
    CHECK(compile_ops, bc.code.size() == 4 && bc.code[0].op == Op::PUSH &&
          bc.code[0].num == 2 && bc.code[1].op == Op::ADD);
    CHECK(disasm_basic,
          disassemble(bc) == "0000 push 2\n0001 add\n0002 print\n0003 halt\n");
    std::string wire = serialize(bc);
    Bytecode back;
    bool ok = deserialize(wire, back);
    CHECK(serialize_roundtrip, ok && disassemble(back) == disassemble(bc));

    // ---- end-to-end programs: ordinary inputs ----
    CHECK(run_arith,
          run("push 7\npush 3\nadd\nprint\npush 7\npush 3\nsub\nprint\n"
              "push 6\npush 5\nmul\nprint\npush 20\npush 6\ndiv\nprint\n"
              "push 20\npush 6\nmod\nprint\nhalt\n") ==
          "10\n4\n30\n3\n2\n");
    CHECK(run_add_saturates,
          run("push 9223372036854775807\npush 1\nadd\nprint\nhalt\n") ==
          "9223372036854775807\n");
    CHECK(run_strings,
          run("str \"hello\"\nlen\nprint\nstr \"a\"\nstr \"b\"\nconcat\nprint\nhalt\n") ==
          "5\nab\n");
    CHECK(run_bools,
          run("true\nnot\nprint\ntrue\nfalse\nand\nprint\nfalse\ntrue\nor\nprint\nhalt\n") ==
          "false\nfalse\ntrue\n");
    CHECK(run_compare,
          run("push 3\npush 5\nlt\nprint\npush 5\npush 3\nge\nprint\n"
              "push 2\npush 2\neq\nprint\nhalt\n") == "true\ntrue\ntrue\n");
    CHECK(run_stack,
          run("push 1\npush 2\nswap\nprint\nprint\npush 5\ndup\nprint\nprint\nhalt\n") ==
          "1\n2\n5\n5\n");
    CHECK(run_vars,
          run("push 9\nset x\nget x\nprint\nhalt\n") == "9\n");
    CHECK(run_jumps,
          run("push 1\njz skip\npush 7\nprint\nskip:\npush 2\njnz done\n"
              "push 8\nprint\ndone:\nhalt\n") == "7\n");
    CHECK(run_arrays,
          run("arrnew\n push 10\napush\n push 20\napush\n dup\nlen\nprint\n"
              " push 0\naget\nprint\nhalt\n") == "2\n10\n");
    return 0;
}
