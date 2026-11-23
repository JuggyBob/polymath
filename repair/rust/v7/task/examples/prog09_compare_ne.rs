#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print 1 != 2; print 2 != 2;").unwrap());
}
