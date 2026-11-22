#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print true;").unwrap());
    print!("{}", minivm::run("print false;").unwrap());
    print!("{}", minivm::run("print null;").unwrap());
    print!("{}", minivm::run("print !true;").unwrap());
    print!("{}", minivm::run("print 7;").unwrap());
    print!("{}", minivm::run("print !0;").unwrap());
    print!("{}", minivm::run("print 8;").unwrap());
    print!("{}", minivm::run("print 1 < 2;").unwrap());
    print!("{}", minivm::run("print 9;").unwrap());
    print!("{}", minivm::run("print 2 <= 2;").unwrap());
    print!("{}", minivm::run("print 10;").unwrap());
    print!("{}", minivm::run("print 3 > 1;").unwrap());
    print!("{}", minivm::run("print 11;").unwrap());
    print!("{}", minivm::run("print 2 == 2;").unwrap());
}
