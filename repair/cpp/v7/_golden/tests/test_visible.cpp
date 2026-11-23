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

static Ins mki(int64_t num, Op op) {
    Ins i;
    i.op = op;
    i.num = num;
    return i;
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
    expect_run("prog01_arith", R"V7SRC(print 2 + 3 * 4; print (2 + 3) * 4; print 10 - 3 - 2; print 7 / 2; print -5 + 9;)V7SRC", S({49,52,10,50,48,10,53,10,51,10,52,10}));
    expect_run("prog02_strings", R"V7SRC(print "hello"; print "a" + "b" + "c"; print "x" + 7; print len("abcd"); print "line1\nline2"; print "q\"q"; print "back\\slash";)V7SRC", S({104,101,108,108,111,10,97,98,99,10,120,55,10,52,10,108,105,110,101,49,10,108,105,110,101,50,10,113,34,113,10,98,97,99,107,92,115,108,97,115,104,10}));
    expect_run("prog03_values", R"V7SRC(print true; print false; print null; print !true; print !0; print 1 < 2; print 2 <= 2; print 3 > 1; print 2 == 2;)V7SRC", S({116,114,117,101,10,102,97,108,115,101,10,110,117,108,108,10,102,97,108,115,101,10,116,114,117,101,10,116,114,117,101,10,116,114,117,101,10,116,114,117,101,10,116,114,117,101,10}));
    expect_run("prog04_variables", R"V7SRC(let a = 4; let b = a + 3; set b = b * 2; print a; print b;)V7SRC", S({52,10,49,52,10}));
    expect_run("prog05_arrays", R"V7SRC(let a = [1, 3]; print a; print a[0]; print a[2]; print len(a); push a, 9; print a;)V7SRC", S({91,49,44,32,51,93,10,49,10,110,117,108,108,10,50,10,91,49,44,32,51,44,32,57,93,10}));
    expect_run("prog06_if", R"V7SRC(let flag = true; if flag { print "yes"; } else { print "no"; } if false { print "bad"; } print "done";)V7SRC", S({121,101,115,10,100,111,110,101,10}));
    expect_run("prog07_while", R"V7SRC(let i = 0; while i < 3 { print i; set i = i + 1; })V7SRC", S({48,10,49,10,50,10}));
    expect_run("prog08_compare_ge", R"V7SRC(print 3 >= 3; print 2 >= 5;)V7SRC", S({116,114,117,101,10,102,97,108,115,101,10}));
    expect_run("prog09_compare_ne", R"V7SRC(print 1 != 2; print 2 != 2;)V7SRC", S({116,114,117,101,10,102,97,108,115,101,10}));
    expect_run("prog10_escape_nul", R"V7SRC(print "a\0b"; print len("a\0b");)V7SRC", S({97,0,98,10,51,10}));
    expect_run("prog11_escape_tab", R"V7SRC(print "a\tb"; print len("a\tb");)V7SRC", S({97,9,98,10,51,10}));
    expect_run("prog12_cmp_chain", R"V7SRC(print 1 < 2 == true; print 2 <= 2 == true;)V7SRC", S({116,114,117,101,10,116,114,117,101,10}));
    expect_run("prog13_unary_chain", R"V7SRC(print - - 3; print ! ! true; print -5 / 2;)V7SRC", S({51,10,116,114,117,101,10,45,50,10}));
    expect_run("prog14_nested_index", R"V7SRC(let a = [[1, 2], [3, 4]]; print a[1][0]; print a[0][1];)V7SRC", S({51,10,50,10}));
    expect_run("prog15_truthy", R"V7SRC(if "" { print "x"; } else { print "y"; } if [] { print "a"; } else { print "b"; } if 0 { print "c"; } else { print "d"; })V7SRC", S({121,10,98,10,100,10}));
    expect_run("prog16_str_cmp", R"V7SRC(print "b" < "aa"; print "aa" < "b"; print "a" == "a";)V7SRC", S({102,97,108,115,101,10,116,114,117,101,10,116,114,117,101,10}));
    expect_run("prog17_add_vars", R"V7SRC(let a = "x"; let b = "y"; print a + b; print "n=" + 5;)V7SRC", S({120,121,10,110,61,53,10}));
    expect_run("prog18_print_repeat", R"V7SRC(print 1; print 1; print 2;)V7SRC", S({49,10,49,10,50,10}));
    expect_run("prog19_len_unicode", R"V7SRC(print len("é"); print len("abc"); print len("😀");)V7SRC", S({49,10,51,10,49,10}));
    expect_run("prog20_negative_index", R"V7SRC(let a = [1, 2]; print a[-1]; print a[5];)V7SRC", S({110,117,108,108,10,110,117,108,108,10}));
    expect_run("prog21_push_sequence", R"V7SRC(let a = [1]; push a, 2; push a, 3; print a;)V7SRC", S({91,49,44,32,50,44,32,51,93,10}));
    expect_run("prog22_empty_then", R"V7SRC(if true { } else { print "e"; } while false { print "z"; } print "ok";)V7SRC", S({111,107,10}));
    expect_run("prog23_nested_while", R"V7SRC(let i = 0; while i < 2 { print i; set i = i + 1; let j = 0; while j < 2 { print 9; set j = j + 1; } })V7SRC", S({48,10,57,10,57,10,49,10,57,10,57,10}));
    expect_run("prog24_array3", R"V7SRC(print [1, 2, 3]; print []; print [[1], [2, 3]];)V7SRC", S({91,49,44,32,50,44,32,51,93,10,91,93,10,91,91,49,93,44,32,91,50,44,32,51,93,93,10}));
    expect_run("prog25_null_eq", R"V7SRC(print null == null; print null != 0; print null == false;)V7SRC", S({116,114,117,101,10,116,114,117,101,10,102,97,108,115,101,10}));
    expect_run("prog26_distinct_basic", R"V7SRC(print distinct([1, 2, 3]); print distinct([1, 2, 1]); print distinct([]);)V7SRC", S({116,114,117,101,10,102,97,108,115,101,10,116,114,117,101,10}));
    expect_run("prog27_distinct_types", R"V7SRC(print distinct(["a", "b"]); print distinct([true, false, true]); print distinct([1, "1"]);)V7SRC", S({116,114,117,101,10,102,97,108,115,101,10,116,114,117,101,10}));
    expect_run("prog28_fiber_basic", R"V7SRC(fiber w { print 1; yield; print 2; } let f = spawn w; print 3; join f; print 4;)V7SRC", S({51,10,49,10,50,10,52,10}));
    expect_run("prog29_fiber_yield", R"V7SRC(fiber a { print "a1"; yield; print "a2"; } fiber b { print "b1"; yield; print "b2"; } spawn a; spawn b; yield; yield;)V7SRC", S({97,49,10,98,49,10,97,50,10,98,50,10}));
    expect_run("prog30_fiber_join_halted", R"V7SRC(fiber w { print 7; } let f = spawn w; yield; join f; print 8;)V7SRC", S({55,10,56,10}));
    {
        MiniVM vm = MiniVM::from_source(R"V7SRC(let x = 5; print x + 1;)V7SRC");
        MiniVM back; bool ok = safe_restore(snapshot(vm), back);
        CHECK("prog31_snapshot_roundtrip", ok && back.run() == S({54,10}));
    }
    {
        std::vector<uint8_t> b(36, 0); b[0]='X'; b[1]='X'; b[2]='X'; b[3]='X';
        std::string got;
        try { restore(b); } catch (const MiniVMError& err) { got = std::string(err.what()) + "\n"; }
        CHECK("prog32_snapshot_badmagic", got == S({66,65,68,95,77,65,71,73,67,10}));
    }

    expect_run("prog33_array_alias", R"V7SRC(let a = [1]; let b = a; push b, 2; print a; print b;)V7SRC", S({91,49,44,32,50,93,10,91,49,44,32,50,93,10}));
    expect_run("prog34_distinct_nested", R"V7SRC(print distinct([[1], [1]]); print distinct([[1], [2]]);)V7SRC", S({102,97,108,115,101,10,116,114,117,101,10}));
    expect_run("prog35_str_cmp_unicode", R"V7SRC(print "é" > "z"; print "é" == "é";)V7SRC", S({116,114,117,101,10,116,114,117,101,10}));
    {
        minivm::Bytecode bc = minivm::compile_source(R"V7SRC(print "a" + "b"; print true;)V7SRC");
        std::string wire = minivm::serialize(bc);
        minivm::Bytecode back;
        bool ok = minivm::deserialize(wire, back);
        CHECK("prog36_serial_roundtrip", ok && minivm::execute(back).output == S({97,98,10,116,114,117,101,10}));
    }
    {
        minivm::Bytecode bc = minivm::compile_source(R"V7SRC(print distinct([1, 2]);)V7SRC");
        std::string text = minivm::disassemble(bc);
        CHECK("prog37_disasm_distinct", text.find("DISTINCT") != std::string::npos);
    }
    {
        minivm::MiniVM vm = minivm::MiniVM::from_source(R"V7SRC(fiber a { print 1; yield; print 2; } spawn a; yield;)V7SRC");
        minivm::MiniVM back; bool ok = safe_restore(minivm::snapshot(vm), back);
        CHECK("prog38_snapshot_fibers", ok && back.run() == S({49,10,50,10}));
    }
    { std::vector<uint8_t> b(36, 0); b[0]='M'; b[1]='V'; b[2]='7'; b[3]=9;
      std::string got; try { restore(b); } catch (const MiniVMError& e) { got = std::string(e.what()) + "\n"; }
      CHECK("prog39_snapshot_badversion", got == S({66,65,68,95,86,69,82,83,73,79,78,10})); }
    { std::vector<uint8_t> g = good_bytes(); g.resize(g.size() - 3);
      std::string got; try { restore(g); } catch (const MiniVMError& e) { got = std::string(e.what()) + "\n"; }
      CHECK("prog40_snapshot_truncated", got == S({84,82,85,78,67,65,84,69,68,10})); }
    { std::vector<uint8_t> g = good_bytes(); g[g.size()-1] ^= 0x01;
      std::string got; try { restore(g); } catch (const MiniVMError& e) { got = std::string(e.what()) + "\n"; }
      CHECK("prog41_snapshot_badchecksum", got == S({66,65,68,95,67,72,69,67,75,83,85,77,10})); }
    {
      minivm::MiniVM vm = minivm::MiniVM::from_source(R"V7SRC(fiber a { print 1; } fiber b { print 2; } spawn a; spawn b;)V7SRC");
      vm.fibers.clear();
      minivm::Fiber fa; fa.id = 1; vm.fibers.push_back(fa);
      minivm::Fiber fb; fb.id = 1; vm.fibers.push_back(fb);
      std::vector<uint8_t> g = snapshot(vm);
      std::string got; try { restore(g); } catch (const MiniVMError& e) { got = std::string(e.what()) + "\n"; }
      CHECK("prog42_snapshot_duplicate", got == S({68,85,80,76,73,67,65,84,69,95,70,73,66,69,82,10}));
    }
    {
        minivm::Bytecode bc;
        bc.code.push_back(mki(0, Op::GET));
        bc.code.push_back(mki(0, Op::PRINT));
        bc.code.push_back(mki(0, Op::HALT));
        CHECK("prog43_load_uninit", execute(bc).output == S({110,117,108,108,10}));
    }
    {
        minivm::Bytecode bc;
        bc.code.push_back(mki(1, Op::PUSH));
        bc.code.push_back(mki(0, Op::DUP));
        bc.code.push_back(mki(0, Op::ADD));
        bc.code.push_back(mki(0, Op::PRINT));
        bc.code.push_back(mki(3, Op::PUSH));
        bc.code.push_back(mki(9, Op::PUSH));
        bc.code.push_back(mki(0, Op::SWAP));
        bc.code.push_back(mki(0, Op::PRINT));
        bc.code.push_back(mki(0, Op::PRINT));
        bc.code.push_back(mki(0, Op::HALT));
        CHECK("prog44_stack_ops", execute(bc).output == S({50,10,51,10,57,10}));
    }
    {
        minivm::Bytecode bc = minivm::compile_source(R"V7SRC(fiber a { print 1; } spawn a; join 1; print 2;)V7SRC");
        std::string wire = minivm::serialize(bc);
        minivm::Bytecode back;
        bool ok = minivm::deserialize(wire, back);
        CHECK("prog45_serial_fibers", ok && minivm::execute(back).output == S({49,10,50,10}));
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
