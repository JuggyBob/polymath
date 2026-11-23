#[path = "../src/lib.rs"]
mod minivm;
use minivm::opcode;
fn main() {
    let code = minivm::compile_source("print \"a\" + \"b\"; print true;").unwrap();
    let text = opcode::serialize(&code);
    let back = match opcode::deserialize(&text) {
        Ok(c) => c,
        Err(_) => { print!("FAIL\n"); return; }
    };
    print!("{}", minivm::vm::execute(&back).unwrap());
}
