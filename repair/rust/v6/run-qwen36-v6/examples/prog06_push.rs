#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "let a = [1]; push a, 2; print a; print len(a);";
    print!("{}", minivm::run(src).unwrap());
}
