#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let code = minivm::compile_source("print 1 + 2;").unwrap();
    print!("{}", minivm::opcode::disassemble(&code));
}
