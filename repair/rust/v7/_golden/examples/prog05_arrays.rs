#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("let a = [1, 3]; print a; print a[0]; print a[2]; print len(a); push a, 9; print a;").unwrap());
}
