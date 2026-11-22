#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print 2 + 3 * 4;").unwrap());
    print!("{}", minivm::run("print (2 + 3) * 4;").unwrap());
    print!("{}", minivm::run("print 10 - 3 - 2;").unwrap());
    print!("{}", minivm::run("print 7 / 2;").unwrap());
    print!("{}", minivm::run("print -5 + 9;").unwrap());
}
