#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("fiber w { print 7; } let f = spawn w; yield; join f; print 8;").unwrap());
}
