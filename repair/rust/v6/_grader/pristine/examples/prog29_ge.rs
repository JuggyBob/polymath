#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "print 3 >= 2;\nprint 2 >= 3;\nprint 2 <= 2;\nprint 8;\nprint 3 > 2;";
    print!("{}", minivm::run(src).unwrap());
}
