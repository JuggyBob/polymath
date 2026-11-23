#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print \"a\\tb\"; print len(\"a\\tb\");").unwrap());
}
