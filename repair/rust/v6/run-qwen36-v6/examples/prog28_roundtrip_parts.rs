#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let big = "print \"a\" + \"b\"; print true; let i = 0; while i < 2 { print i; set i = i + 1; }";
    print!("{}", minivm::opcode::disassemble(&minivm::compile_source(big).unwrap()));
    let small = "let x = 4; print x + 1;";
    let c = minivm::compile_source(small).unwrap();
    let back = minivm::opcode::deserialize(&minivm::opcode::serialize(&c)).unwrap();
    print!("{}", minivm::opcode::disassemble(&back));
}
