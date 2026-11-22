#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "print \"b\" < \"a\";\nprint 0;\nprint \"a\" < \"bb\";\nprint 1;\nprint \"bbb\" > \"a\";";
    print!("{}", minivm::run(src).unwrap());
}
