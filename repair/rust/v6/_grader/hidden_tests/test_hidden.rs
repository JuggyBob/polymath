#[path = "../src/lib.rs"]
mod minivm;

use minivm::opcode::{self, Opcode};
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

fn check_exec(name: &str, code: &[Opcode], expected: &str) {
    match minivm::vm::execute(code) {
        Ok(out) => check_eq(name, out, expected),
        Err(_) => println!("TEST {} FAIL", name),
    }
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
    check_run("h_distinct_basic", "print distinct([1, 2, 3]);\nprint distinct([1, 2, 1]);", "true\nfalse\n");
    check_run("h_distinct_types", "print distinct([\"a\", \"b\"]);\nprint distinct([true, false, true]);", "true\nfalse\n");
    check_run("h_ge_lexer", "print 3 >= 3;\nprint 2 >= 5;", "true\nfalse\n");
    check_run("h_ne_lexer", "print 1 != 2;\nprint 2 != 2;", "true\nfalse\n");
    check_run("h_escape_nul", "print \"a\\0b\";", "a\0b\n");
    check_run("h_escape_tab", "print \"a\\tb\";", "a\tb\n");
    check_run("h_cmp_chain", "print 1 < 2 == true;", "true\n");
    check_run("h_unary_chain", "print - - 3;", "3\n");
    check_run("h_nested_index", "let a = [[1, 2], [3, 4]]; print a[1][0];", "3\n");
    check_run("h_truthy_empty_string", "if \"\" { print \"x\"; } else { print \"y\"; }", "y\n");
    check_run("h_str_cmp", "print \"b\" < \"aa\";", "false\n");
    check_run("h_add_vars", "let a = \"x\"; let b = \"y\"; print a + b;", "xy\n");
    check_run("h_print_repeat", "print 1; print 1;", "1\n1\n");
    check_run("h_len_unicode", "print len(\"é\");", "1\n");
    check_run("h_negative_index", "let a = [1, 2]; print a[-1];", "null\n");
    check_run("h_push_sequence", "let a = [1]; push a, 2; push a, 3; print a;", "[1, 2, 3]\n");
    check_run("h_empty_then", "if true { } else { print \"e\"; }", "");
    check_run("h_nested_while", "let i = 0; while i < 2 { print i; set i = i + 1; let j = 0; while j < 2 { print 9; set j = j + 1; } }", "0\n9\n9\n1\n9\n9\n");
    check_run("h_array3", "print [1, 2, 3];", "[1, 2, 3]\n");
    check_run("h_null_eq", "print null == null;", "true\n");
    // DISTINCT end to end: lexer, parser, compiler, VM, disassembler, serialiser.
    let dc = minivm::compile_source("print distinct([1, 2]);");
    match dc {
        Ok(code) => {
            check_exec("h_distinct_exec", &code, "true\n");
            let text = opcode::serialize(&code);
            match opcode::deserialize(&text) {
                Ok(back) => check_exec("h_distinct_roundtrip", &back, "true\n"),
                Err(_) => println!("TEST h_distinct_roundtrip FAIL"),
            }
            let dis = opcode::disassemble(&code);
            if dis.contains("DISTINCT") { println!("TEST h_distinct_disasm PASS"); }
            else { println!("TEST h_distinct_disasm FAIL"); }
        }
        Err(_) => {
            println!("TEST h_distinct_exec FAIL");
            println!("TEST h_distinct_roundtrip FAIL");
            println!("TEST h_distinct_disasm FAIL");
        }
    }

    // Serialise -> deserialise -> execute across every opcode family.
    let sc = minivm::compile_source("print \"a\" + \"b\"; print true; print false; let i = 0; while i < 2 { print i; set i = i + 1; }");
    match sc {
        Ok(code) => match opcode::deserialize(&opcode::serialize(&code)) {
            Ok(back) => check_exec("h_serial_full", &back, "ab\ntrue\nfalse\n0\n1\n"),
            Err(_) => println!("TEST h_serial_full FAIL"),
        },
        Err(_) => println!("TEST h_serial_full FAIL"),
    }

    // Raw bytecode behaviours.
    let raw = vec![Opcode::Load(0), Opcode::Print, Opcode::Halt];
    check_exec("h_load_uninit", &raw, "null\n");
    let raw2 = vec![Opcode::PushInt(1), Opcode::Dup, Opcode::Add, Opcode::Print,
                    Opcode::PushInt(3), Opcode::PushInt(9), Opcode::Swap,
                    Opcode::Print, Opcode::Print, Opcode::Halt];
    check_exec("h_stack_ops", &raw2, "2\n3\n9\n");

    // Performance: correctness preserved, complexity differs.
    let big_loop = "let i = 0; while i < 30000 { print i; set i = i + 1; }";
    perf("perf_print", 15.0, || { let _ = black_box(minivm::run(big_loop)); });
    let big_code: Vec<Opcode> = (0..10000).map(|i| Opcode::PushInt(i)).collect();
    perf("perf_disasm", 20.0, || { black_box(opcode::disassemble(&big_code)); });
}
