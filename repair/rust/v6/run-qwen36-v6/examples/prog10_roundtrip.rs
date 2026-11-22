#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let code = minivm::compile_source("let x = 4; print x + 1; print \"hi\";").unwrap();
    let text = minivm::opcode::serialize(&code);
    let back = minivm::opcode::deserialize(&text).unwrap();
    print!("{}", minivm::opcode::disassemble(&back));
}
