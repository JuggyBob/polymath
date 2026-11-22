#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("if \"\" { print \"x\"; } else { print \"y\"; }").unwrap());
}
