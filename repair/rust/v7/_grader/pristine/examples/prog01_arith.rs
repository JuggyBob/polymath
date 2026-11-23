#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print 2 + 3 * 4; print (2 + 3) * 4; print 10 - 3 - 2; print 7 / 2; print -5 + 9;").unwrap());
}
