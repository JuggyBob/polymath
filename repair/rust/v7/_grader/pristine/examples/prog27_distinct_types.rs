#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print distinct([\"a\", \"b\"]); print distinct([true, false, true]); print distinct([1, \"1\"]);").unwrap());
}
