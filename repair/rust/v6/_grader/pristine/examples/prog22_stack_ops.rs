#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    use minivm::opcode::Opcode;
    let code = vec![Opcode::PushInt(1), Opcode::Dup, Opcode::Add, Opcode::Print,
                    Opcode::PushInt(3), Opcode::PushInt(9), Opcode::Swap,
                    Opcode::Print, Opcode::Print, Opcode::Halt];
    print!("{}", minivm::vm::execute(&code).unwrap());
}
