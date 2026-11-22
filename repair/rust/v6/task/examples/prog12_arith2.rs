#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print 7 % 3;").unwrap());
    print!("{}", minivm::run("print 10 / 3;").unwrap());
    print!("{}", minivm::run("print 6 * 7;").unwrap());
}
