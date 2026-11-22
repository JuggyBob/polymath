#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    match minivm::compile_source("print distinct([1, 2]);") {
        Ok(code) => {
            let text = minivm::opcode::serialize(&code);
            match minivm::opcode::deserialize(&text) {
                Ok(back) => match minivm::vm::execute(&back) {
                    Ok(out) => print!("{}", out),
                    Err(_) => println!("ERROR"),
                },
                Err(_) => println!("ERROR"),
            }
        }
        Err(_) => println!("ERROR"),
    }
}
