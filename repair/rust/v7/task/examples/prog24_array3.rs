#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print [1, 2, 3]; print []; print [[1], [2, 3]];").unwrap());
}
