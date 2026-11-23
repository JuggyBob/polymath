#[path = "../src/lib.rs"]
mod minivm;
use minivm::opcode;
fn main() {
    let code = minivm::compile_source("print distinct([1, 2]);").unwrap();
    let text = opcode::disassemble(&code);
    if text.contains("DISTINCT") { print!("DISTINCT\n"); }
    else { print!("MISSING\n"); }
}
