#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("let i = 0; while i < 3 { print i; set i = i + 1; }").unwrap());
}
