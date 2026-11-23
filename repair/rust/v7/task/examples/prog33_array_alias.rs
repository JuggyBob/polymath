#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("let a = [1]; let b = a; push b, 2; print a; print b;").unwrap());
}
