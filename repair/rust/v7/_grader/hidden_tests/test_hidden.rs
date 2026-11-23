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

fn check_exec(name: &str, code: &Code, expected: &str) {
    match minivm::vm::execute(code) {
        Ok(out) => check_eq(name, out, expected),
        Err(_) => println!("TEST {} FAIL", name),
    }
}

fn check_serial(name: &str, src: &str, expected: &str) {
    let code = match minivm::compile_source(src) {
        Ok(c) => c,
        Err(_) => { println!("TEST {} FAIL", name); return; }
    };
    let back = match opcode::deserialize(&opcode::serialize(&code)) {
        Ok(c) => c,
        Err(_) => { println!("TEST {} FAIL", name); return; }
    };
    check_exec(name, &back, expected);
}

fn check_snapshot(name: &str, src: &str, expected: &str) {
    let vm = match MiniVM::from_source(src) {
        Ok(v) => v,
        Err(_) => { println!("TEST {} FAIL", name); return; }
    };
    let bytes = vm.snapshot();
    let vm2 = match restore(&bytes) {
        Ok(v) => v,
        Err(_) => { println!("TEST {} FAIL", name); return; }
    };
    let mut vm2 = vm2;
    match vm2.run() {
        Ok(out) => check_eq(name, out, expected),
        Err(_) => println!("TEST {} FAIL", name),
    }
}

fn check_error(name: &str, got: Result<MiniVM, String>, expected: &str) {
    match got {
        Ok(_) => println!("TEST {} FAIL", name),
        Err(e) => check_eq(name, e, expected),
    }
}

fn good_bytes() -> Vec<u8> {
    match MiniVM::from_source("let x = 5; print x + 1;") {
        Ok(vm) => vm.snapshot(),
        Err(_) => Vec::new(),
    }
}

fn compiled_or_empty(src: &str) -> Code {
    minivm::compile_source(src).unwrap_or_else(|_| Code { main: Vec::new(), fibers: Vec::new() })
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
    check_run("h_arith_precedence", "print 2 + 3 * 4 - 5; print 20 / 3 / 2; print -7 / 2;", "9\n3\n-3\n");
    check_run("h_str_concat_mixed", "print \"a\" + 1 + true; print null + \"x\";", "a1true\nnullx\n");
    check_run("h_escape_backslash", "print \"a\\\\b\"; print len(\"a\\\\b\");", "a\\b\n3\n");
    check_run("h_escape_quote", "print \"say \\\"hi\\\"\";", "say \"hi\"\n");
    check_run("h_ge_chain", "print 3 >= 3 == true; print 2 >= 5 == false;", "true\ntrue\n");
    check_run("h_ne_chain", "print 1 != 2 == true; print 2 != 2 == false;", "true\ntrue\n");
    check_run("h_ge_lexer", "print 4 >= 4; print 5 >= 9;", "true\nfalse\n");
    check_run("h_ne_lexer", "print 8 != 9; print 8 != 8;", "true\nfalse\n");
    check_run("h_lt_and_gt", "print 1 < 2; print 2 > 1; print 1 > 2; print 2 < 1;", "true\ntrue\nfalse\nfalse\n");
    check_run("h_le_and_ge", "print 1 <= 1; print 1 >= 1; print 1 <= 0; print 1 >= 2;", "true\ntrue\nfalse\nfalse\n");
    check_run("h_cmp_chain", "print 1 < 2 == true; print 2 <= 3 == true;", "true\ntrue\n");
    check_run("h_unary_chain", "print - - - 4; print ! ! ! false;", "-4\ntrue\n");
    check_run("h_nested_index", "let a = [[[1, 2]]]; print a[0][0][1];", "2\n");
    check_run("h_array_alias", "let a = [1]; let b = a; push b, 2; print a; print b;", "[1, 2]\n[1, 2]\n");
    check_run("h_distinct_structural", "print distinct([[1], [1]]); print distinct([[1], [2]]);", "false\ntrue\n");
    check_run("h_distinct_mixed", "print distinct([1, \"1\", true]); print distinct([null, null]);", "true\nfalse\n");
    check_run("h_truthy_empty_string", "if \"\" { print \"x\"; } else { print \"y\"; }", "y\n");
    check_run("h_truthy_empty_array", "if [] { print \"x\"; } else { print \"y\"; }", "y\n");
    check_run("h_truthy_values", "if 0 { print \"a\"; } else { print \"b\"; } if null { print \"c\"; } else { print \"d\"; } if \"s\" { print \"e\"; }", "b\nd\ne\n");
    check_run("h_str_cmp", "print \"b\" < \"aa\"; print \"aa\" < \"b\"; print \"abc\" == \"abc\";", "false\ntrue\ntrue\n");
    check_run("h_str_cmp_unicode", "print \"é\" > \"z\"; print \"é\" == \"é\";", "true\ntrue\n");
    check_run("h_add_vars", "let a = \"x\"; let b = \"y\"; print a + b;", "xy\n");
    check_run("h_print_repeat", "print 1; print 1; print 1;", "1\n1\n1\n");
    check_run("h_len_unicode", "print len(\"😀\"); print len(\"a\\tb\");", "1\n3\n");
    check_run("h_negative_index", "let a = [1, 2, 3]; print a[-1]; print a[9];", "null\nnull\n");
    check_run("h_push_sequence", "let a = [1]; push a, 2; push a, 3; push a, 4; print a;", "[1, 2, 3, 4]\n");
    check_run("h_empty_then", "if true { } else { print \"e\"; } print \"z\";", "z\n");
    check_run("h_nested_while", "let i = 0; while i < 2 { print i; set i = i + 1; let j = 0; while j < 2 { print 9; set j = j + 1; } }", "0\n9\n9\n1\n9\n9\n");
    check_run("h_array3", "print [1, 2, 3];", "[1, 2, 3]\n");
    check_run("h_null_eq", "print null == null; print null != null; print null == 0;", "true\nfalse\nfalse\n");
    check_run("h_fiber_three", "fiber a { print 1; yield; print 4; } fiber b { print 2; yield; print 5; } fiber c { print 3; yield; print 6; } spawn a; spawn b; spawn c; yield;", "1\n2\n3\n4\n5\n6\n");
    check_run("h_fiber_join_wait", "fiber w { print 1; yield; print 2; } let f = spawn w; join f; print 3;", "1\n2\n3\n");
    check_run("h_fiber_join_two_waiters", "fiber w { yield; print 9; } fiber a { yield; print \"a\"; } fiber b { yield; print \"b\"; } spawn w; spawn a; spawn b; yield;", "9\na\nb\n");
    check_run("h_fiber_yield_noop", "fiber a { yield; print 1; } spawn a; join 1; print 2;", "1\n2\n");

    let dc = compiled_or_empty("print distinct([1, 2]);");
    check_exec("h_distinct_exec", &dc, "true\n");
    check_serial("h_distinct_roundtrip", "print distinct([1, 2]);", "true\n");
    if opcode::disassemble(&dc).contains("DISTINCT") {
        println!("TEST h_distinct_disasm PASS");
    } else {
        println!("TEST h_distinct_disasm FAIL");
    }
    check_serial("h_serial_full", "print \"a\" + \"b\"; print true; print false; let i = 0; while i < 2 { print i; set i = i + 1; }", "ab\ntrue\nfalse\n0\n1\n");
    check_serial("h_serial_fibers", "fiber a { print 1; } spawn a; join 1; print 2;", "1\n2\n");

    check_snapshot("h_snapshot_roundtrip_run", "let x = 5; print x + 1;", "6\n");
    check_snapshot("h_snapshot_globals", "let a = [1, 2]; let s = \"hi\"; print len(a) + len(s);", "4\n");
    check_snapshot("h_snapshot_fibers", "fiber a { print 1; yield; print 2; } spawn a; yield;", "1\n2\n");

    let mut bad_magic = b"NOPE".to_vec();
    bad_magic.extend(std::iter::repeat(0u8).take(32));
    check_error("h_snapshot_badmagic", restore(&bad_magic), "BAD_MAGIC");

    let mut bad_version = b"MV7".to_vec();
    bad_version.push(9);
    bad_version.extend(std::iter::repeat(0u8).take(32));
    check_error("h_snapshot_badversion", restore(&bad_version), "BAD_VERSION");

    let gb = good_bytes();
    check_error("h_snapshot_truncated", restore(&gb[..gb.len() - 3]), "TRUNCATED");

    let mut cb = gb.clone();
    let last = cb.len() - 1;
    cb[last] ^= 0x01;
    check_error("h_snapshot_badchecksum", restore(&cb), "BAD_CHECKSUM");

    check_error("h_snapshot_duplicate_fiber", restore(&duplicate_fiber_bytes()), "DUPLICATE_FIBER");

    check_exec("h_load_uninit", &Code { main: vec![Opcode::Load(0), Opcode::Print, Opcode::Halt], fibers: Vec::new() }, "null\n");
    check_exec("h_stack_ops", &Code {
        main: vec![
            Opcode::PushInt(1), Opcode::Dup, Opcode::Add, Opcode::Print,
            Opcode::PushInt(3), Opcode::PushInt(9), Opcode::Swap,
            Opcode::Print, Opcode::Print, Opcode::Halt,
        ],
        fibers: Vec::new(),
    }, "2\n3\n9\n");

    let loop_src = "let i = 0; while i < 60000 { print i; set i = i + 1; }";
    perf("perf_print", 60.0, || { black_box(minivm::run(loop_src)); });
    let big_code: Vec<Opcode> = (0..20000).map(Opcode::PushInt).collect();
    perf("perf_disasm", 50.0, || { black_box(opcode::disassemble(&Code { main: big_code.clone(), fibers: Vec::new() })); });
    let snap_code = compiled_or_empty("print 1;");
    perf("perf_snapshot", 60.0, || {
        let mut vm = minivm::vm::Vm::new(snap_code.clone());
        for i in 0..2000 {
            vm.globals.push((format!("g{}", i), minivm::value::Value::Int(i)));
        }
        let b = minivm::snapshot::snapshot(&vm);
        black_box(minivm::snapshot::restore(&b));
    });
}
