#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("if \"\" { print \"x\"; } else { print \"y\"; } if [] { print \"a\"; } else { print \"b\"; } if 0 { print \"c\"; } else { print \"d\"; }").unwrap());
}
