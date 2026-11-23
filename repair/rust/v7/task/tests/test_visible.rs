#[path = "../src/lib.rs"]
mod minivm;

use minivm::opcode::{self, Code, Opcode};
use minivm::{restore, MiniVM};
use std::hint::black_box;
use std::time::Instant;

fn check_run(name: &str, src: &str, expected: &str) {
    match minivm::run(src) {
        Ok(out) if out == expected => println!("TEST {} PASS", name),
        _ => println!("TEST {} FAIL", name),
    }
}

fn check_eq(name: &str, got: String, expected: &str) {
    if got == expected {
        println!("TEST {} PASS", name);
    } else {
        println!("TEST {} FAIL", name);
    }
}

fn check_err(name: &str, got: Result<MiniVM, String>, expected: &str) {
    match got {
        Ok(_) => println!("TEST {} FAIL", name),
        Err(e) => check_eq(name, e, expected),
    }
}

fn check_exec(name: &str, code: &Code, expected: &str) {
    match minivm::vm::execute(code) {
        Ok(out) => check_eq(name, out, expected),
        Err(_) => println!("TEST {} FAIL", name),
    }
}

fn duplicate_fiber_bytes() -> Vec<u8> {
    let mut b = Vec::new();
    b.extend_from_slice(b"MV7");
    b.push(1);
    b.extend_from_slice(&1u32.to_le_bytes());
    b.push(31);
    b.extend_from_slice(&0u32.to_le_bytes());
    b.extend_from_slice(&0u32.to_le_bytes());
    b.extend_from_slice(&2u32.to_le_bytes());
    for _ in 0..2 {
        b.extend_from_slice(&1u32.to_le_bytes());
        b.extend_from_slice(&0u32.to_le_bytes());
        b.extend_from_slice(&0u32.to_le_bytes());
        b.push(0);
        b.extend_from_slice(&0u32.to_le_bytes());
    }
    b.extend_from_slice(&0u32.to_le_bytes());
    b.extend_from_slice(&0u32.to_le_bytes());
    let mut h: u32 = 0x811c9dc5;
    for &x in &b {
        h ^= x as u32;
        h = h.wrapping_mul(0x01000193);
    }
    b.extend_from_slice(&h.to_le_bytes());
    b
}

fn perf(name: &str, limit_ms: f64, mut work: impl FnMut()) {
    for _ in 0..3 {
        let t = Instant::now();
        work();
        let ms = t.elapsed().as_secs_f64() * 1000.0;
        let ok = if ms <= limit_ms { "PASS" } else { "FAIL" };
        println!("PERF {} {:.3} {}", name, ms, ok);
    }
}

fn main() {
    check_run("prog01_arith", "print 2 + 3 * 4; print (2 + 3) * 4; print 10 - 3 - 2; print 7 / 2; print -5 + 9;", "14\n20\n5\n3\n4\n");
    check_run("prog02_strings", "print \"hello\"; print \"a\" + \"b\" + \"c\"; print \"x\" + 7; print len(\"abcd\"); print \"line1\\nline2\"; print \"q\\\"q\"; print \"back\\\\slash\";", "hello\nabc\nx7\n4\nline1\nline2\nq\"q\nback\\slash\n");
    check_run("prog03_values", "print true; print false; print null; print !true; print !0; print 1 < 2; print 2 <= 2; print 3 > 1; print 2 == 2;", "true\nfalse\nnull\nfalse\ntrue\ntrue\ntrue\ntrue\ntrue\n");
    check_run("prog04_variables", "let a = 4; let b = a + 3; set b = b * 2; print a; print b;", "4\n14\n");
    check_run("prog05_arrays", "let a = [1, 3]; print a; print a[0]; print a[2]; print len(a); push a, 9; print a;", "[1, 3]\n1\nnull\n2\n[1, 3, 9]\n");
    check_run("prog06_if", "let flag = true; if flag { print \"yes\"; } else { print \"no\"; } if false { print \"bad\"; } print \"done\";", "yes\ndone\n");
    check_run("prog07_while", "let i = 0; while i < 3 { print i; set i = i + 1; }", "0\n1\n2\n");
    check_run("prog08_compare_ge", "print 3 >= 3; print 2 >= 5;", "true\nfalse\n");
    check_run("prog09_compare_ne", "print 1 != 2; print 2 != 2;", "true\nfalse\n");
    check_run("prog10_escape_nul", "print \"a\\0b\"; print len(\"a\\0b\");", "a\0b\n3\n");
    check_run("prog11_escape_tab", "print \"a\\tb\"; print len(\"a\\tb\");", "a\tb\n3\n");
    check_run("prog12_cmp_chain", "print 1 < 2 == true; print 2 <= 2 == true;", "true\ntrue\n");
    check_run("prog13_unary_chain", "print - - 3; print ! ! true; print -5 / 2;", "3\ntrue\n-2\n");
    check_run("prog14_nested_index", "let a = [[1, 2], [3, 4]]; print a[1][0]; print a[0][1];", "3\n2\n");
    check_run("prog15_truthy", "if \"\" { print \"x\"; } else { print \"y\"; } if [] { print \"a\"; } else { print \"b\"; } if 0 { print \"c\"; } else { print \"d\"; }", "y\nb\nd\n");
    check_run("prog16_str_cmp", "print \"b\" < \"aa\"; print \"aa\" < \"b\"; print \"a\" == \"a\";", "false\ntrue\ntrue\n");
    check_run("prog17_add_vars", "let a = \"x\"; let b = \"y\"; print a + b; print \"n=\" + 5;", "xy\nn=5\n");
    check_run("prog18_print_repeat", "print 1; print 1; print 2;", "1\n1\n2\n");
    check_run("prog19_len_unicode", "print len(\"é\"); print len(\"abc\"); print len(\"😀\");", "1\n3\n1\n");
    check_run("prog20_negative_index", "let a = [1, 2]; print a[-1]; print a[5];", "null\nnull\n");
    check_run("prog21_push_sequence", "let a = [1]; push a, 2; push a, 3; print a;", "[1, 2, 3]\n");
    check_run("prog22_empty_then", "if true { } else { print \"e\"; } while false { print \"z\"; } print \"ok\";", "ok\n");
    check_run("prog23_nested_while", "let i = 0; while i < 2 { print i; set i = i + 1; let j = 0; while j < 2 { print 9; set j = j + 1; } }", "0\n9\n9\n1\n9\n9\n");
    check_run("prog24_array3", "print [1, 2, 3]; print []; print [[1], [2, 3]];", "[1, 2, 3]\n[]\n[[1], [2, 3]]\n");
    check_run("prog25_null_eq", "print null == null; print null != 0; print null == false;", "true\ntrue\nfalse\n");
    check_run("prog26_distinct_basic", "print distinct([1, 2, 3]); print distinct([1, 2, 1]); print distinct([]);", "true\nfalse\ntrue\n");
    check_run("prog27_distinct_types", "print distinct([\"a\", \"b\"]); print distinct([true, false, true]); print distinct([1, \"1\"]);", "true\nfalse\ntrue\n");
    check_run("prog28_fiber_basic", "fiber w { print 1; yield; print 2; } let f = spawn w; print 3; join f; print 4;", "3\n1\n2\n4\n");
    check_run("prog29_fiber_yield", "fiber a { print \"a1\"; yield; print \"a2\"; } fiber b { print \"b1\"; yield; print \"b2\"; } spawn a; spawn b; yield; yield;", "a1\nb1\na2\nb2\n");
    check_run("prog30_fiber_join_halted", "fiber w { print 7; } let f = spawn w; yield; join f; print 8;", "7\n8\n");
    {
        let out = match MiniVM::from_source("let x = 5; print x + 1;") {
            Ok(vm) => match restore(&vm.snapshot()) {
                Ok(mut back) => back.run().unwrap_or_else(|_| "FAIL".to_string()),
                Err(_) => "FAIL".to_string(),
            },
            Err(_) => "FAIL".to_string(),
        };
        check_eq("prog31_snapshot_roundtrip", out, "6\n");
    }
    {
        let mut b = b"XXXX".to_vec();
        b.extend(std::iter::repeat(0u8).take(32));
        check_err("prog32_snapshot_badmagic", restore(&b), "BAD_MAGIC");
    }
    check_run("prog33_array_alias", "let a = [1]; let b = a; push b, 2; print a; print b;", "[1, 2]\n[1, 2]\n");
    check_run("prog34_distinct_nested", "print distinct([[1], [1]]); print distinct([[1], [2]]);", "false\ntrue\n");
    check_run("prog35_str_cmp_unicode", "print \"é\" > \"z\"; print \"é\" == \"é\";", "true\ntrue\n");
    {
        let out = match minivm::compile_source("print \"a\" + \"b\"; print true;") {
            Ok(c) => match opcode::deserialize(&opcode::serialize(&c)) {
                Ok(back) => minivm::vm::execute(&back).unwrap_or_else(|_| "FAIL".to_string()),
                Err(_) => "FAIL".to_string(),
            },
            Err(_) => "FAIL".to_string(),
        };
        check_eq("prog36_serial_roundtrip", out, "ab\ntrue\n");
    }
    {
        let out = match minivm::compile_source("print distinct([1, 2]);") {
            Ok(c) => {
                if opcode::disassemble(&c).contains("DISTINCT") {
                    "DISTINCT\n".to_string()
                } else {
                    "MISSING\n".to_string()
                }
            }
            Err(_) => "MISSING\n".to_string(),
        };
        check_eq("prog37_disasm_distinct", out, "DISTINCT\n");
    }
    {
        let src = "fiber a { print 1; yield; print 2; } spawn a; yield;";
        let out = match MiniVM::from_source(src) {
            Ok(vm) => match restore(&vm.snapshot()) {
                Ok(mut back) => back.run().unwrap_or_else(|_| "FAIL".to_string()),
                Err(_) => "FAIL".to_string(),
            },
            Err(_) => "FAIL".to_string(),
        };
        check_eq("prog38_snapshot_fibers", out, "1\n2\n");
    }
    {
        let mut b = b"MV7".to_vec();
        b.push(9);
        b.extend(std::iter::repeat(0u8).take(32));
        check_err("prog39_snapshot_badversion", restore(&b), "BAD_VERSION");
    }
    let good = match MiniVM::from_source("let x = 5; print x + 1;") {
        Ok(vm) => vm.snapshot(),
        Err(_) => Vec::new(),
    };
    check_err("prog40_snapshot_truncated", restore(&good[..good.len() - 3]), "TRUNCATED");
    {
        let mut b = good.clone();
        let last = b.len() - 1;
        b[last] ^= 0x01;
        check_err("prog41_snapshot_badchecksum", restore(&b), "BAD_CHECKSUM");
    }
    check_err("prog42_snapshot_duplicate", restore(&duplicate_fiber_bytes()), "DUPLICATE_FIBER");
    check_exec("prog43_load_uninit", &Code {
        main: vec![Opcode::Load(0), Opcode::Print, Opcode::Halt],
        fibers: Vec::new(),
    }, "null\n");
    check_exec("prog44_stack_ops", &Code {
        main: vec![
            Opcode::PushInt(1), Opcode::Dup, Opcode::Add, Opcode::Print,
            Opcode::PushInt(3), Opcode::PushInt(9), Opcode::Swap,
            Opcode::Print, Opcode::Print, Opcode::Halt,
        ],
        fibers: Vec::new(),
    }, "2\n3\n9\n");
    {
        let src = "fiber a { print 1; } spawn a; join 1; print 2;";
        let out = match minivm::compile_source(src) {
            Ok(c) => match opcode::deserialize(&opcode::serialize(&c)) {
                Ok(back) => minivm::vm::execute(&back).unwrap_or_else(|_| "FAIL".to_string()),
                Err(_) => "FAIL".to_string(),
            },
            Err(_) => "FAIL".to_string(),
        };
        check_eq("prog45_serial_fibers", out, "1\n2\n");
    }

    let loop_src = "let i = 0; while i < 2000 { print i; set i = i + 1; }";
    perf("perf_print", 60.0, || { black_box(minivm::run(loop_src)); });
    let big_code: Vec<Opcode> = (0..2000).map(Opcode::PushInt).collect();
    perf("perf_disasm", 50.0, || { black_box(opcode::disassemble(&Code { main: big_code.clone(), fibers: Vec::new() })); });
    let snap_src = "print 1;";
    let snap_code = minivm::compile_source(snap_src).unwrap_or_else(|_| Code { main: vec![opcode::Opcode::Halt], fibers: Vec::new() });
    perf("perf_snapshot", 60.0, || {
        let mut vm = minivm::vm::Vm::new(snap_code.clone());
        for i in 0..200 {
            vm.globals.push((format!("g{}", i), minivm::value::Value::Int(i)));
        }
        let b = minivm::snapshot::snapshot(&vm);
        black_box(minivm::snapshot::restore(&b));
    });
}
