#[path = "../src/lib.rs"]
mod minivm;
use minivm::restore;
use minivm::MiniVM;
fn main() {
    let vm = MiniVM::from_source("let x = 5; print x + 1;").unwrap();
    let bytes = vm.snapshot();
    let restored = restore(&bytes).unwrap();
    let mut restored = restored;
    print!("{}", restored.run().unwrap());
}
