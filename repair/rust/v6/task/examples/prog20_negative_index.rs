#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print [][0];\nprint 0;\nprint [1, 2][-5];").unwrap());
}
