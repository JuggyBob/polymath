#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("let a = \"x\"; let b = \"y\"; print a + b; print \"n=\" + 5;").unwrap());
}
