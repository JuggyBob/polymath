#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "let i = 0; while i < 2 { print i; set i = i + 1; let j = 0; while j < 1 { print 9; set j = j + 1; } }";
    print!("{}", minivm::run(src).unwrap());
}
