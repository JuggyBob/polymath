#[path = "../src/lib.rs"]
mod minivm;
use minivm::{restore, MiniVM};
fn main() {
    let good = MiniVM::from_source("let x = 5; print x + 1;").unwrap().snapshot();
    let b = &good[..good.len() - 3];
    match restore(&b) {
        Ok(_) => print!("OK\n"),
        Err(e) => print!("{}\n", e),
    }
}
