#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print len(\"é\");").unwrap());
}
