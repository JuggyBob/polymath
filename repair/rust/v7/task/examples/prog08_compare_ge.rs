#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print 3 >= 3; print 2 >= 5;").unwrap());
}
