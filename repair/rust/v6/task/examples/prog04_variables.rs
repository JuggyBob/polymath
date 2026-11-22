#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "let a = 10; let b = 3; print a + b; print a - b; set a = 6; print a; print a * b;";
    print!("{}", minivm::run(src).unwrap());
}
