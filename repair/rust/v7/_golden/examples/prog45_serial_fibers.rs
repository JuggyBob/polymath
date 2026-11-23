#[path = "../src/lib.rs"]
mod minivm;
use minivm::opcode;
fn main() {
    let code = minivm::compile_source("fiber a { print 1; } spawn a; join 1; print 2;").unwrap();
    let text = opcode::serialize(&code);
    let back = match opcode::deserialize(&text) {
        Ok(c) => c,
        Err(_) => { print!("FAIL\n"); return; }
    };
    print!("{}", minivm::vm::execute(&back).unwrap());
}
