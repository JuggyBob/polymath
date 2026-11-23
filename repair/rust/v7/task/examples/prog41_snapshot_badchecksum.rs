#[path = "../src/lib.rs"]
mod minivm;
use minivm::{restore, MiniVM};
fn main() {
    let good = MiniVM::from_source("let x = 5; print x + 1;").unwrap().snapshot();
    let mut b = good.clone();
    let last = b.len() - 1;
    b[last] ^= 0x01;
    match restore(&b) {
        Ok(_) => print!("OK\n"),
        Err(e) => print!("{}\n", e),
    }
}
