#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("fiber w { print 1; yield; print 2; } let f = spawn w; print 3; join f; print 4;").unwrap());
}
