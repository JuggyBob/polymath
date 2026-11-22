#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "let i = 0; while i < 3 { print i; set i = i + 1; } print \"end\";";
    print!("{}", minivm::run(src).unwrap());
}
