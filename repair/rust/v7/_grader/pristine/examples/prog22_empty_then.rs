#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("if true { } else { print \"e\"; } while false { print \"z\"; } print \"ok\";").unwrap());
}
