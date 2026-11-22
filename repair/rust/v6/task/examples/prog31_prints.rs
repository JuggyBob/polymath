#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "print 1;\nprint 2;\nprint 1;\nprint 3;";
    print!("{}", minivm::run(src).unwrap());
}
