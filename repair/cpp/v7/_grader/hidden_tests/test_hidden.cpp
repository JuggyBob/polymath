#include <chrono>

#include <cstdint>
#include <iostream>
#include <string>
#include <vector>

#include "bytecode.h"
#include "compiler.h"
#include "disasm.h"
#include "lexer.h"
#include "parser.h"
#include "serialize.h"
#include "snapshot.h"
#include "util.h"
#include "vm.h"

#define CHECK(name, cond) \
    std::cout << "TEST " << name << " " << ((cond) ? "PASS" : "FAIL") << "\n"
#define PERF(name, ms, limit) \
    std::cout << "PERF " << name << " " << (ms) << " " \
              << (((ms) < (limit)) ? "PASS" : "FAIL") << "\n"

using namespace minivm;

static const double LIMIT_PRINT = 60.0;
static const double LIMIT_DISASM = 50.0;
static const double LIMIT_SNAPSHOT = 60.0;

static std::string S(const std::vector<int>& v) {
    std::string s;
    for (std::size_t i = 0; i < v.size(); ++i) s += static_cast<char>(v[i]);
    return s;
}

static double now_ms() {
    return std::chrono::duration<double, std::milli>(
               std::chrono::steady_clock::now().time_since_epoch()).count();
}

static void expect_run(const char* name, const std::string& src, const std::string& want) {
    std::string got;
    try { got = run(src); } catch (...) { got = "<EXCEPTION>"; }
    CHECK(name, got == want);
}

static Ins mk(Op op, int64_t num = 0, const std::string& text = "") {
    Ins i;
    i.op = op;
    i.num = num;
    i.text = text;
    return i;
}

static std::vector<uint8_t> good_bytes() {
    return snapshot(MiniVM::from_source("let x = 5; print x + 1;"));
}

static bool safe_restore(const std::vector<uint8_t>& bytes, MiniVM& out) {
    try { out = restore(bytes); return true; } catch (...) { return false; }
}

int main() {
    std::cout << std::unitbuf;
    expect_run("h_arith_precedence", R"V7SRC(print 2 + 3 * 4 - 5; print 20 / 3 / 2; print -7 / 2;)V7SRC", S({57,10,51,10,45,51,10}));
    expect_run("h_str_concat_mixed", R"V7SRC(let hash = "a#b"; print "a" + 1 + true; print null + "x";)V7SRC", S({97,49,116,114,117,101,10,110,117,108,108,120,10}));
    expect_run("h_escape_backslash", R"V7SRC(print "a\\b"; print len("a\\b");)V7SRC", S({97,92,98,10,51,10}));
    expect_run("h_escape_quote", R"V7SRC(print "say \"hi\"";)V7SRC", S({115,97,121,32,34,104,105,34,10}));
    expect_run("h_ge_chain", R"V7SRC(print 3 >= 3 == true; print 2 >= 5 == false;)V7SRC", S({116,114,117,101,10,116,114,117,101,10}));
    expect_run("h_ne_chain", R"V7SRC(print 1 != 2 == true; print 2 != 2 == false;)V7SRC", S({116,114,117,101,10,116,114,117,101,10}));
    {
        std::vector<Token> toks = lex(">=");
        std::string ge_out;
        try { ge_out = run("print 4 >= 4; print 5 >= 9;"); } catch (...) { ge_out = "<EXCEPTION>"; }
        CHECK("h_ge_lexer", ge_out == S({116,114,117,101,10,102,97,108,115,101,10})
              && !toks.empty() && toks[0].kind == Tok::Ge);
    }
    {
        std::vector<Token> toks = lex("!=");
        std::string ne_out;
        try { ne_out = run("print 8 != 9; print 8 != 8;"); } catch (...) { ne_out = "<EXCEPTION>"; }
        CHECK("h_ne_lexer", ne_out == S({116,114,117,101,10,102,97,108,115,101,10})
              && !toks.empty() && toks[0].kind == Tok::Ne);
    }
    expect_run("h_lt_and_gt", R"V7SRC(print 1 < 2; print 2 > 1; print 1 > 2; print 2 < 1;)V7SRC", S({116,114,117,101,10,116,114,117,101,10,102,97,108,115,101,10,102,97,108,115,101,10}));
    expect_run("h_le_and_ge", R"V7SRC(print 1 <= 1; print 1 >= 1; print 1 <= 0; print 1 >= 2;)V7SRC", S({116,114,117,101,10,116,114,117,101,10,102,97,108,115,101,10,102,97,108,115,101,10}));
    expect_run("h_cmp_chain", R"V7SRC(print 1 < 2 == true; print 2 <= 3 == true;)V7SRC", S({116,114,117,101,10,116,114,117,101,10}));
    expect_run("h_unary_chain", R"V7SRC(print - - - 4; print ! ! ! false;)V7SRC", S({45,52,10,116,114,117,101,10}));
    expect_run("h_nested_index", R"V7SRC(let a = [[[1, 2]]]; print a[0][0][1];)V7SRC", S({50,10}));
    expect_run("h_array_alias", R"V7SRC(let a = [1]; let b = a; push b, 2; print a; print b;)V7SRC", S({91,49,44,32,50,93,10,91,49,44,32,50,93,10}));
    expect_run("h_distinct_structural", R"V7SRC(print distinct([[1], [1]]); print distinct([[1], [2]]);)V7SRC", S({102,97,108,115,101,10,116,114,117,101,10}));
    expect_run("h_distinct_mixed", R"V7SRC(print distinct([1, "1", true]); print distinct([null, null]);)V7SRC", S({116,114,117,101,10,102,97,108,115,101,10}));
    expect_run("h_truthy_empty_string", R"V7SRC(if "" { print "x"; } else { print "y"; })V7SRC", S({121,10}));
    expect_run("h_truthy_empty_array", R"V7SRC(if [] { print "x"; } else { print "y"; })V7SRC", S({121,10}));
    expect_run("h_truthy_values", R"V7SRC(if 0 { print "a"; } else { print "b"; } if null { print "c"; } else { print "d"; } if "s" { print "e"; })V7SRC", S({98,10,100,10,101,10}));
    expect_run("h_str_cmp", R"V7SRC(print "b" < "aa"; print "aa" < "b"; print "abc" == "abc";)V7SRC", S({102,97,108,115,101,10,116,114,117,101,10,116,114,117,101,10}));
    expect_run("h_str_cmp_unicode", R"V7SRC(print "é" > "z"; print "é" == "é";)V7SRC", S({116,114,117,101,10,116,114,117,101,10}));
    {
        (void)run("let prime = 1; print prime;");
        std::string add_out;
        try { add_out = run(R"V7SRC(let a = "x"; let b = "y"; print a + b;)V7SRC"); }
        catch (...) { add_out = "<EXCEPTION>"; }
        Bytecode shifted = compile_source("let z = 9; print z;");
        bool idx_ok = true;
        for (std::size_t i = 0; i < shifted.code.size(); ++i)
            if ((shifted.code[i].op == Op::SET || shifted.code[i].op == Op::GET)
                && shifted.code[i].num != 0) idx_ok = false;
        CHECK("h_add_vars", add_out == S({120,121,10}) && idx_ok);
    }
    {
        std::string r1 = run("print 1; print 1; print 1;");
        std::string r2 = run("print 1; print 1; print 1;");
        CHECK("h_print_repeat", r1 == S({49,10,49,10,49,10}) && r2 == S({49,10,49,10,49,10}));
    }
    expect_run("h_len_unicode", R"V7SRC(print len("😀"); print len("a\tb");)V7SRC", S({49,10,51,10}));
    expect_run("h_negative_index", R"V7SRC(let a = [1, 2, 3]; print a[-1]; print a[9];)V7SRC", S({110,117,108,108,10,110,117,108,108,10}));
    expect_run("h_push_sequence", R"V7SRC(let a = [1]; push a, 2; push a, 3; push a, 4; print a;)V7SRC", S({91,49,44,32,50,44,32,51,44,32,52,93,10}));
    expect_run("h_empty_then", R"V7SRC(if true { } else { print "e"; } print "z";)V7SRC", S({122,10}));
    expect_run("h_nested_while", R"V7SRC(let i = 0; while i < 2 { print i; set i = i + 1; let j = 0; while j < 2 { print 9; set j = j + 1; } })V7SRC", S({48,10,57,10,57,10,49,10,57,10,57,10}));
    expect_run("h_array3", R"V7SRC(print [1, 2, 3];)V7SRC", S({91,49,44,32,50,44,32,51,93,10}));
    expect_run("h_null_eq", R"V7SRC(print null == null; print null != null; print null == 0;)V7SRC", S({116,114,117,101,10,102,97,108,115,101,10,102,97,108,115,101,10}));
    expect_run("h_fiber_three", R"V7SRC(fiber a { print 1; yield; print 4; } fiber b { print 2; yield; print 5; } fiber c { print 3; yield; print 6; } spawn a; spawn b; spawn c; yield;)V7SRC", S({49,10,50,10,51,10,52,10,53,10,54,10}));
    expect_run("h_fiber_join_wait", R"V7SRC(fiber w { print 1; yield; print 2; } let f = spawn w; join f; print 3;)V7SRC", S({49,10,50,10,51,10}));
    expect_run("h_fiber_join_two_waiters", R"V7SRC(fiber w { yield; print 9; } fiber a { yield; print "a"; } fiber b { yield; print "b"; } spawn w; spawn a; spawn b; yield;)V7SRC", S({57,10,97,10,98,10}));
    expect_run("h_fiber_yield_noop", R"V7SRC(fiber w { print 1; } fiber b { yield; } spawn w; spawn b; yield; join 1; print 2;)V7SRC", S({49,10,50,10}));
    expect_run("h_distinct_exec", R"V7SRC(print distinct([1, 2]);)V7SRC", S({116,114,117,101,10}));
    {
        Bytecode bc = compile_source(R"V7SRC(print distinct([1, 2]);)V7SRC");
        std::string wire = serialize(bc);
        Bytecode back;
        bool ok = deserialize(wire, back);
        CHECK("h_distinct_roundtrip", ok && execute(back).output == S({116,114,117,101,10}));
    }
    {
        Bytecode bc = compile_source(R"V7SRC(print distinct([1, 2]);)V7SRC");
        std::string wire = serialize(bc);
        Bytecode back;
        bool ok = deserialize(wire, back);
        CHECK("h_distinct_disasm", ok && disassemble(back).find("DISTINCT") != std::string::npos);
    }
    {
        Bytecode bc = compile_source(R"V7SRC(print "a" + "b"; print true; print false; let i = 0; while i < 2 { print i; set i = i + 1; })V7SRC");
        std::string wire = serialize(bc);
        Bytecode back;
        bool ok = deserialize(wire, back);
        CHECK("h_serial_full", ok && execute(back).output == S({97,98,10,116,114,117,101,10,102,97,108,115,101,10,48,10,49,10}));
    }
    {
        Bytecode bc = compile_source(R"V7SRC(fiber a { print 1; } spawn a; join 1; print 2;)V7SRC");
        std::string wire = serialize(bc);
        Bytecode back;
        bool ok = deserialize(wire, back);
        CHECK("h_serial_fibers", ok && execute(back).output == S({49,10,50,10}));
    }
    {
        MiniVM vm = MiniVM::from_source(R"V7SRC(let x = 5; let flag = true; let big = 4294967297; if flag { if big > 4294967296 { print x + 1; } })V7SRC");
        (void)vm.run();
        vm.output.clear();
        vm.fibers[0].pc = 0;
        vm.fibers[0].halted = false;
        MiniVM back; bool ok = safe_restore(snapshot(vm), back);
        MiniVM vm2 = MiniVM::from_source("print y;");
        vm2.globals[0] = Value(static_cast<int64_t>(7));
        MiniVM back2; bool ok2 = safe_restore(snapshot(vm2), back2);
        CHECK("h_snapshot_roundtrip_run", ok && ok2 && back.run() == S({54,10})
              && back2.run() == S({55,10}));
    }
    {
        MiniVM vm = MiniVM::from_source(R"V7SRC(let a = [1, 2]; let s = "hi"; print len(a) + len(s);)V7SRC");
        MiniVM back; bool ok = safe_restore(snapshot(vm), back);
        MiniVM sep1 = MiniVM::from_source("let first = 1;");
        MiniVM sep2 = MiniVM::from_source("let second = 2;");
        CHECK("h_snapshot_globals", ok && back.run() == S({52,10})
              && sep1.global_names.size() == 1 && sep2.global_names.size() == 1);
    }
    {
        MiniVM vm = MiniVM::from_source(R"V7SRC(fiber a { print 1; yield; print 2; } spawn a; yield;)V7SRC");
        MiniVM back; bool ok = safe_restore(snapshot(vm), back);
        CHECK("h_snapshot_fibers", ok && back.run() == S({49,10,50,10}));
    }
    { std::vector<uint8_t> b(36, 0); b[0]='N'; b[1]='O'; b[2]='P'; b[3]='E';
      std::string got; try { restore(b); } catch (const MiniVMError& e) { got = e.what(); }
      CHECK("h_snapshot_badmagic", got == S({66,65,68,95,77,65,71,73,67})); }
    { std::vector<uint8_t> b(36, 0); b[0]='M'; b[1]='V'; b[2]='7'; b[3]=9;
      std::string got; try { restore(b); } catch (const MiniVMError& e) { got = e.what(); }
      CHECK("h_snapshot_badversion", got == S({66,65,68,95,86,69,82,83,73,79,78})); }
    { std::vector<uint8_t> g = good_bytes(); g.resize(g.size() - 3);
      std::string got; try { restore(g); } catch (const MiniVMError& e) { got = e.what(); }
      CHECK("h_snapshot_truncated", got == S({84,82,85,78,67,65,84,69,68})); }
    { std::vector<uint8_t> g = good_bytes(); g[g.size()-1] ^= 0x01;
      std::string got; try { restore(g); } catch (const MiniVMError& e) { got = e.what(); }
      CHECK("h_snapshot_badchecksum", got == S({66,65,68,95,67,72,69,67,75,83,85,77})); }
    {
      MiniVM vm = MiniVM::from_source(R"V7SRC(fiber a { print 1; } fiber b { print 2; } spawn a; spawn b;)V7SRC");
      vm.fibers.clear();
      Fiber fa; fa.id = 1; vm.fibers.push_back(fa);
      Fiber fb; fb.id = 1; vm.fibers.push_back(fb);
      std::vector<uint8_t> g = snapshot(vm);
      std::string got; try { restore(g); } catch (const MiniVMError& e) { got = e.what(); }
      CHECK("h_snapshot_duplicate_fiber", got == S({68,85,80,76,73,67,65,84,69,95,70,73,66,69,82}));
    }
    {
        Bytecode bc;
        bc.code.push_back(mk(Op::GET, 0));
        bc.code.push_back(mk(Op::PRINT));
        bc.code.push_back(mk(Op::HALT));
        std::string hex = hex_encode(std::string("\x00\x01", 2));
        const uint8_t hash_input[3] = {1, 2, 3};
        bool hash_ok = fnv1a(hash_input, 3) == 0x56cf37abu;
        CHECK("h_load_uninit", execute(bc).output == S({110,117,108,108,10})
              && hex == "0001" && hash_ok);
    }
    {
        Bytecode bc;
        bc.code.push_back(mk(Op::PUSH, 1));
        bc.code.push_back(mk(Op::DUP));
        bc.code.push_back(mk(Op::ADD));
        bc.code.push_back(mk(Op::PRINT));
        bc.code.push_back(mk(Op::PUSH, 3));
        bc.code.push_back(mk(Op::PUSH, 9));
        bc.code.push_back(mk(Op::SWAP));
        bc.code.push_back(mk(Op::PRINT));
        bc.code.push_back(mk(Op::PRINT));
        bc.code.push_back(mk(Op::HALT));
        Bytecode bc2;
        bc2.global_names.push_back("x");
        bc2.global_names.push_back("y");
        bc2.code.push_back(mk(Op::PUSH, 7));
        bc2.code.push_back(mk(Op::SET, 0, "y"));
        bc2.code.push_back(mk(Op::GET, 0, "x"));
        bc2.code.push_back(mk(Op::PRINT));
        bc2.code.push_back(mk(Op::HALT));
        CHECK("h_stack_ops", execute(bc).output == S({50,10,51,10,57,10})
              && execute(bc2).output == S({55,10}));
    }

    // ===== performance (exactly 3 runs per workload) =====
    {
        std::string src = "let i = 0; while i < 60000 { print i; set i = i + 1; }";
        for (int r = 0; r < 3; ++r) {
            double t0 = now_ms();
            std::string out = run(src);
            double ms = now_ms() - t0;
            PERF("perf_print", ms, LIMIT_PRINT);
            (void)out;
        }
    }
    {
        Bytecode big;
        big.code.reserve(20000);
        for (int i = 0; i < 20000; ++i) big.code.push_back(mk(Op::PUSH, i));
        for (int r = 0; r < 3; ++r) {
            double t0 = now_ms();
            std::string text = disassemble(big);
            double ms = now_ms() - t0;
            PERF("perf_disasm", ms, LIMIT_DISASM);
            (void)text;
        }
    }
    {
        MiniVM vm;
        for (int i = 0; i < 2000; ++i) {
            vm.global_names.push_back("g" + std::to_string(i));
            vm.globals.push_back(Value(static_cast<int64_t>(i)));
        }
        for (int i = 0; i < 200; ++i) vm.code.code.push_back(mk(Op::PUSH, i));
        Fiber f; f.id = 0; vm.fibers.push_back(f);
        for (int r = 0; r < 3; ++r) {
            double t0 = now_ms();
            std::vector<uint8_t> b = snapshot(vm);
            MiniVM back;
            safe_restore(b, back);
            double ms = now_ms() - t0;
            PERF("perf_snapshot", ms, LIMIT_SNAPSHOT);
            (void)back;
        }
    }

    return 0;
}
