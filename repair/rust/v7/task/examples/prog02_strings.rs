#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print \"hello\"; print \"a\" + \"b\" + \"c\"; print \"x\" + 7; print len(\"abcd\"); print \"line1\\nline2\"; print \"q\\\"q\"; print \"back\\\\slash\";").unwrap());
}
