#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print null == null; print null != 0; print null == false;").unwrap());
}
