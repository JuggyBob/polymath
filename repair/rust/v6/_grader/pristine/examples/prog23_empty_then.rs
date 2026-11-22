#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "if true { print \"t\"; } else { print \"e\"; } if false { } else { print \"e\"; }";
    print!("{}", minivm::run(src).unwrap());
}
