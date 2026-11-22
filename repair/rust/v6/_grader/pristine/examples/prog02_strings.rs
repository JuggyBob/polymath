#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print \"hello\";").unwrap());
    print!("{}", minivm::run("print \"a\" + \"b\" + \"c\";").unwrap());
    print!("{}", minivm::run("print \"x\" + 7;").unwrap());
    print!("{}", minivm::run("print len(\"abcd\");").unwrap());
    print!("{}", minivm::run("print \"line1\\nline2\";").unwrap());
    print!("{}", minivm::run("print \"q\\\"q\";").unwrap());
    print!("{}", minivm::run("print \"back\\\\slash\";").unwrap());
}
