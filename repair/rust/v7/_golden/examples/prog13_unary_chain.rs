#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print - - 3; print ! ! true; print -5 / 2;").unwrap());
}
