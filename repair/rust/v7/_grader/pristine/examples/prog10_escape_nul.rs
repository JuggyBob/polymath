#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print \"a\\0b\"; print len(\"a\\0b\");").unwrap());
}
