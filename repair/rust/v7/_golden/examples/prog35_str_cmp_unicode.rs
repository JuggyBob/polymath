#[path = "../src/lib.rs"]
mod minivm;
fn main() {
    print!("{}", minivm::run("print \"é\" > \"z\"; print \"é\" == \"é\";").unwrap());
}
