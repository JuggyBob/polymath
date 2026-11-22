#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print \\"a\\0b\\";\\nprint \\"a\\tb\\";").unwrap());
}
