#include <chrono>
#include <cstdint>
#include <iostream>
#include <limits>
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
#define PERF(name, ms, limit) \
    std::cout << "PERF " << #name << " " << (ms) << " " \
              << (((ms) < (limit)) ? "PASS" : "FAIL") << "\n"

using namespace minivm;

static const double LIMIT_DISASM = 18.0;
static const double LIMIT_VARS = 55.0;

static double now_ms() {
    return std::chrono::duration<double, std::milli>(
               std::chrono::steady_clock::now().time_since_epoch()).count();
}

static bool expect_run(const char* name, const std::string& src,
                       const std::string& want) {
    bool ok = (run(src) == want);
    std::cout << "TEST " << name << " " << (ok ? "PASS" : "FAIL") << "\n";
    return ok;
}

static Ins mk(Op op, int64_t num = 0, const std::string& text = "") {
    Ins i;
    i.op = op;
    i.num = num;
    i.text = text;
    return i;
}

int main() {
    std::cout << std::unitbuf;

    // ===== the DISTINCT operation, layer by layer (each observable alone) =====
    {
        std::vector<Token> t = lex("distinct\n");
        CHECK(test_h_lex_distinct,
              t.size() == 2 && t[0].kind == Tok::Distinct && t[0].text == "distinct");
    }
    {
        std::vector<Token> t(2);
        t[0].kind = Tok::Distinct;
        t[0].text = "distinct";
        t[1].kind = Tok::End;
        std::vector<Node> n = parse(t);
        CHECK(test_h_parse_distinct, n.size() == 1 && n[0].kind == NK::DISTINCT);
    }
    {
        std::vector<Node> n(1);
        n[0].kind = NK::DISTINCT;
        Bytecode bc = compile(n);
        CHECK(test_h_compile_distinct, bc.code.size() == 1 && bc.code[0].op == Op::DISTINCT);
    }
    {
        Bytecode bc;
        bc.code.push_back(mk(Op::PUSH, 1));
        bc.code.push_back(mk(Op::PUSH, 2));
        bc.code.push_back(mk(Op::DISTINCT));
        bc.code.push_back(mk(Op::PRINT));
        bc.code.push_back(mk(Op::HALT));
        CHECK(test_h_execute_distinct, execute(bc).output == "true\n");
    }
    expect_run("test_h_distinct_different", "push 3\npush 4\ndistinct\nprint\nhalt\n", "true\n");
    expect_run("test_h_distinct_equal", "push 3\npush 3\ndistinct\nprint\nhalt\n", "false\n");
    {
        Bytecode bc;
        bc.code.push_back(mk(Op::DISTINCT));
        CHECK(test_h_disasm_distinct, disassemble(bc) == "0000 distinct\n");
    }
    {
        Bytecode bc;
        bc.code.push_back(mk(Op::PUSH, 1));
        bc.code.push_back(mk(Op::PUSH, 2));
        bc.code.push_back(mk(Op::DISTINCT));
        bc.code.push_back(mk(Op::PRINT));
        bc.code.push_back(mk(Op::HALT));
        std::string wire = serialize(bc);
        Bytecode back;
        bool ok = deserialize(wire, back);
        CHECK(test_h_serialize_distinct_roundtrip,
              ok && back.code.size() == 5 && back.code[2].op == Op::DISTINCT &&
              execute(back).output == "true\n");
    }

    // ===== overflow / arithmetic edges =====
    expect_run("test_h_sub_saturates",
               "push -9223372036854775808\npush 1\nsub\nprint\nhalt\n",
               "-9223372036854775808\n");
    expect_run("test_h_mul_saturates",
               "push 9223372036854775807\npush 2\nmul\nprint\nhalt\n",
               "9223372036854775807\n");
    CHECK(test_h_align_exact,
          align_up(8, 8) == 8 && align_up(16, 8) == 16 && align_up(24, 8) == 24);
    CHECK(test_h_to_int_clamps,
          to_int("999999999999999999999999") == std::numeric_limits<int64_t>::max() &&
          to_int("-999999999999999999999999") == std::numeric_limits<int64_t>::min());

    // ===== value semantics edges =====
    expect_run("test_h_truthy_negative",
               "push -1\njz zero\npush 5\nprint\nzero:\nhalt\n", "5\n");
    expect_run("test_h_null_not_zero", "null\npush 0\neq\nprint\nhalt\n", "false\n");
    {
        Value a(std::string("hello"));
        Value b;
        b = std::move(a);
        CHECK(test_h_move_assign_clears_source,
              b.repr() == "hello" && a.repr() == "<moved>");
    }

    // ===== lexer / parser edges =====
    expect_run("test_h_escape_newline", "str \"a\\nb\"\nlen\nprint\nhalt\n", "3\n");
    expect_run("test_h_hash_inside_string", "str \"a#b\"\nprint\nhalt\n", "a#b\n");
    expect_run("test_h_neq", "push 1\npush 2\nneq\nprint\nhalt\n", "true\n");
    expect_run("test_h_label_case_insensitive",
               "push 0\njz Ll\npush 7\nprint\nLL:\npush 8\nprint\nhalt\n", "8\n");
    {
        run("push 1\npush 2\npush 3\nghost:\nhalt\n");
        std::string out = run(
            "push 0\njz ghost\npush 8\nprint\nhalt\n");
        CHECK(test_h_labels_recompiled_clean, out == "");
    }

    // ===== VM edges =====
    expect_run("test_h_ge_equal", "push 5\npush 5\nge\nprint\nhalt\n", "true\n");
    expect_run("test_h_len_null", "null\nlen\nprint\nhalt\n", "0\n");
    expect_run("test_h_div_by_zero", "push 5\npush 0\ndiv\nprint\nhalt\n", "null\n");
    expect_run("test_h_swap_single", "push 4\nswap\nswap\nprint\nhalt\n", "null\n");
    {
        run("push 5\nset alpha\nhalt\n");
        CHECK(test_h_variables_isolated_per_run,
              run("get alpha\nprint\nhalt\n") == "null\n");
    }

    // ===== serialiser edges =====
    {
        Bytecode a;
        a.code.push_back(mk(Op::PUSH, 1));
        std::string s1 = serialize(a);
        Bytecode b;
        b.code.push_back(mk(Op::PUSH, 2));
        std::string s2 = serialize(b);
        CHECK(test_h_serialize_repeatable, s2 == "push 2 -\n" && s1 == "push 1 -\n");
    }
    {
        Bytecode bc;
        bc.code.push_back(mk(Op::PUSH, 6));
        bc.code.push_back(mk(Op::PUSH, 4));
        bc.code.push_back(mk(Op::MOD));
        bc.code.push_back(mk(Op::PRINT));
        bc.code.push_back(mk(Op::HALT));
        std::string wire = serialize(bc);
        Bytecode back;
        bool ok = deserialize(wire, back);
        CHECK(test_h_mod_roundtrip_executes,
              ok && execute(back).output == "2\n");
        CHECK(test_h_disasm_mod, disassemble(back) == "0000 push 6\n0001 push 4\n"
                                                     "0002 mod\n0003 print\n0004 halt\n");
    }
    expect_run("test_h_mod_direct", "push 7\npush 3\nmod\nprint\nhalt\n", "1\n");

    // ===== performance (3 runs each) =====
    {
        Bytecode big;
        big.code.reserve(20000);
        for (int i = 0; i < 20000; ++i) big.code.push_back(mk(Op::PUSH, i));
        for (int r = 0; r < 3; ++r) {
            double t0 = now_ms();
            std::string text = disassemble(big);
            double ms = now_ms() - t0;
            PERF(perf_disasm, ms, LIMIT_DISASM);
            if (text.empty()) CHECK(test_h_disasm_nonempty, false);
        }
    }
    {
        Bytecode big;
        const int kVars = 500;
        for (int i = 0; i < kVars; ++i) {
            big.code.push_back(mk(Op::PUSH, i));
            big.code.push_back(mk(Op::SET, 0, "v" + std::to_string(i)));
        }
        for (int i = 0; i < 60000; ++i) {
            big.code.push_back(mk(Op::GET, 0, "v" + std::to_string(i % kVars)));
            big.code.push_back(mk(Op::POP));
        }
        big.code.push_back(mk(Op::HALT));
        for (int r = 0; r < 3; ++r) {
            double t0 = now_ms();
            VMResult res = execute(big);
            double ms = now_ms() - t0;
            PERF(perf_vars, ms, LIMIT_VARS);
            if (res.steps < 120000) CHECK(test_h_perf_vars_ran, false);
        }
    }
    return 0;
}
