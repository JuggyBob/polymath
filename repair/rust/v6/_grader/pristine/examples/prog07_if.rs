#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "let flag = true; if flag { print \"yes\"; } else { print \"no\"; } if false { print \"bad\"; } print \"done\";";
    print!("{}", minivm::run(src).unwrap());
}
