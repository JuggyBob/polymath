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
    check_run("prog01_arith", "print 2 + 3 * 4;\nprint (2 + 3) * 4;\nprint 10 - 3 - 2;\nprint 7 / 2;\nprint -5 + 9;", "14\n20\n5\n3\n4\n");
    check_run("prog02_strings", "print \"hello\";\nprint \"a\" + \"b\" + \"c\";\nprint \"x\" + 7;\nprint len(\"abcd\");\nprint \"line1\\nline2\";\nprint \"q\\\"q\";\nprint \"back\\\\slash\";", "hello\nabc\nx7\n4\nline1\nline2\nq\"q\nback\\slash\n");
    check_run("prog03_values", "print true;\nprint false;\nprint null;\nprint !true;\nprint 7;\nprint !0;\nprint 8;\nprint 1 < 2;\nprint 9;\nprint 2 <= 2;\nprint 10;\nprint 3 > 1;\nprint 11;\nprint 2 == 2;", "true\nfalse\nnull\nfalse\n7\ntrue\n8\ntrue\n9\ntrue\n10\ntrue\n11\ntrue\n");
    check_run("prog04_variables", "let a = 10; let b = 3; print a + b; print a - b; set a = 6; print a; print a * b;", "13\n7\n6\n18\n");
    check_run("prog05_arrays", "let a = [1, 3]; print a; print a[0]; print a[1]; print len(a); print [9, 8];", "[1, 3]\n1\n3\n2\n[9, 8]\n");
    check_run("prog06_push", "let a = [1]; push a, 2; print a; print len(a);", "[1, 2]\n2\n");
    check_run("prog07_if", "let flag = true; if flag { print \"yes\"; } else { print \"no\"; } if false { print \"bad\"; } print \"done\";", "yes\ndone\n");
    check_run("prog08_while", "let i = 0; while i < 3 { print i; set i = i + 1; } print \"end\";", "0\n1\n2\nend\n");
    check_run("prog11_nested_values", "print [[1, 2]];\nprint [true, null];\nprint [1, 2][1];", "[[1, 2]]\n[true, null]\n2\n");
    check_run("prog12_arith2", "print 7 % 3;\nprint 10 / 3;\nprint 6 * 7;", "1\n3\n42\n");
    let c = minivm::compile_source("print 1 + 2;").unwrap();
    check_eq("prog09_disasm", opcode::disassemble(&c),
        "0000 PUSH_INT 1\n0001 PUSH_INT 2\n0002 ADD\n0003 PRINT\n0004 HALT\n");
    let c2 = minivm::compile_source("let x = 4; print x + 1; print \"hi\";").unwrap();
    let back = opcode::deserialize(&opcode::serialize(&c2)).unwrap();
    check_eq("prog10_roundtrip_exec", minivm::vm::execute(&back).unwrap(), "5\nhi\n");
    let small_loop = "let i = 0; while i < 1200 { print i; set i = i + 1; }";
    perf("vis_print", 400.0, || { black_box(minivm::run(small_loop).unwrap()); });
    let small_code: Vec<Opcode> = (0..250).map(|i| Opcode::PushInt(i)).collect();
    perf("vis_disasm", 400.0, || { black_box(opcode::disassemble(&small_code)); });
}
