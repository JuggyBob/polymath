#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print 1 < 2 == true; print 2 <= 2 == true;").unwrap());
}
