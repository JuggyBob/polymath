#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print len(\"é\"); print len(\"abc\"); print len(\"😀\");").unwrap());
}
