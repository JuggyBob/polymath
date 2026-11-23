#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print true; print false; print null; print !true; print !0; print 1 < 2; print 2 <= 2; print 3 > 1; print 2 == 2;").unwrap());
}
