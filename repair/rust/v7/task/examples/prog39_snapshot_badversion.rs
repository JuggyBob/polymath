#[path = "../src/lib.rs"]
mod minivm;
use minivm::restore;
fn main() {
    let mut b = b"MV7".to_vec();
    b.push(9);
    b.extend(std::iter::repeat(0u8).take(32));
    match restore(&b) {
        Ok(_) => print!("OK\n"),
        Err(e) => print!("{}\n", e),
    }
}
