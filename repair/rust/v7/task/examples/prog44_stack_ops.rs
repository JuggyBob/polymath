#[path = "../src/lib.rs"]
mod minivm;
use minivm::opcode::{Code, Opcode};
fn main() {
    let code = Code {
        main: vec![
            Opcode::PushInt(1), Opcode::Dup, Opcode::Add, Opcode::Print,
            Opcode::PushInt(3), Opcode::PushInt(9), Opcode::Swap,
            Opcode::Print, Opcode::Print, Opcode::Halt,
        ],
        fibers: Vec::new(),
    };
    print!("{}", minivm::vm::execute(&code).unwrap());
}
