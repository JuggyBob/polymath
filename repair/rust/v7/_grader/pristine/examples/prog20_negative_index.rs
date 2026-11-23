#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("let a = [1, 2]; print a[-1]; print a[5];").unwrap());
}
