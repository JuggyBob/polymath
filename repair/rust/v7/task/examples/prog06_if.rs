#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("let flag = true; if flag { print \"yes\"; } else { print \"no\"; } if false { print \"bad\"; } print \"done\";").unwrap());
}
