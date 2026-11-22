#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print len(\"a\\0b\");\nprint len(\"a\\tb\") > len(\"ab\");\nprint \"a\\nb\";").unwrap());
}
