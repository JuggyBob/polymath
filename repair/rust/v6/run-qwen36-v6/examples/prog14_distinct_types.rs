#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    let src = "print distinct([\"a\", \"b\"]);\nprint distinct([true, false, true]);";
    match minivm::run(src) {
        Ok(s) => print!("{}", s),
        Err(e) => println!("ERROR {}", e),
    }
}
