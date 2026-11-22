#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "let a = \"x\"; let b = \"y\"; print \"\" + a + b;";
    print!("{}", minivm::run(src).unwrap());
}
