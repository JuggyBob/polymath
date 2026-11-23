#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("let a = [[1, 2], [3, 4]]; print a[1][0]; print a[0][1];").unwrap());
}
