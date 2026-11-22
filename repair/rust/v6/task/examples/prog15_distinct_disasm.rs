#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    match minivm::compile_source("print distinct([1, 2]);") {
        Ok(code) => print!("{}", minivm::opcode::disassemble(&code)),
        Err(_) => println!("ERROR"),
    }
}
