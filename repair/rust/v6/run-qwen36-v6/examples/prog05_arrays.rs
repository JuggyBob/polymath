#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "let a = [1, 3]; print a; print a[0]; print a[1]; print len(a); print [9, 8];";
    print!("{}", minivm::run(src).unwrap());
}
