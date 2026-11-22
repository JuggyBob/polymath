#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "if \"x\" { print \"s\"; } else { print \"n\"; } if [] { print \"s\"; } else { print \"n\"; } print 0; if 0 { print \"s\"; } else { print \"n\"; }";
    print!("{}", minivm::run(src).unwrap());
}
