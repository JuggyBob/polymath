#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("fiber a { print \"a1\"; yield; print \"a2\"; } fiber b { print \"b1\"; yield; print \"b2\"; } spawn a; spawn b; yield; yield;").unwrap());
}
