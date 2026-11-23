#[path = "../src/lib.rs"]
mod minivm;
use minivm::opcode::{Code, Opcode};
fn main() {
    let code = Code {
        main: vec![Opcode::Load(0), Opcode::Print, Opcode::Halt],
        fibers: Vec::new(),
    };
    print!("{}", minivm::vm::execute(&code).unwrap());
}
