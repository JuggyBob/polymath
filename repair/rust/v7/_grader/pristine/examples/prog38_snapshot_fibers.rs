#[path = "../src/lib.rs"]
mod minivm;
use minivm::{restore, MiniVM};
fn main() {
    let vm = MiniVM::from_source("fiber a { print 1; yield; print 2; } spawn a; yield;").unwrap();
    let bytes = vm.snapshot();
    let mut back = match restore(&bytes) {
        Ok(v) => v,
        Err(_) => { print!("FAIL\n"); return; }
    };
    print!("{}", back.run().unwrap());
}
