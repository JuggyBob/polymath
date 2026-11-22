#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print \"é\";\nprint len(\"abc\");\nprint len(\"é\") < 3;").unwrap());
}
