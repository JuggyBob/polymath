#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "print [7, 7, 7];\nprint len([1, 2, 3]);";
    print!("{}", minivm::run(src).unwrap());
}
