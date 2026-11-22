#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    match minivm::run("print distinct([1, 2, 3]);\nprint distinct([1, 2, 1]);") {
        Ok(s) => print!("{}", s),
        Err(e) => println!("ERROR {}", e),
    }
}
