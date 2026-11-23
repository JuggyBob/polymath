#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print distinct([[1], [1]]); print distinct([[1], [2]]);").unwrap());
}
