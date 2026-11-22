#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    use minivm::opcode::Opcode;
    let code = vec![Opcode::Jump(3), Opcode::PushInt(9), Opcode::Store(0),
                    Opcode::Load(0), Opcode::Print, Opcode::Halt];
    print!("{}", minivm::vm::execute(&code).unwrap());
    print!("{}", minivm::run("let x = 5; print x;").unwrap());
}
