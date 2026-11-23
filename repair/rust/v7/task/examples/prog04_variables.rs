#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("let a = 4; let b = a + 3; set b = b * 2; print a; print b;").unwrap());
}
