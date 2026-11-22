#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print [[1, 2]];").unwrap());
    print!("{}", minivm::run("print [true, null];").unwrap());
    print!("{}", minivm::run("print [1, 2][1];").unwrap());
}
