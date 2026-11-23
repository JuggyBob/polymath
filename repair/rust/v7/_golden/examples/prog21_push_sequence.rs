#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("let a = [1]; push a, 2; push a, 3; print a;").unwrap());
}
