#[path = "../src/lib.rs"]
mod minivm;
use minivm::restore;
fn duplicate_fiber_bytes() -> Vec<u8> {
    let mut b = Vec::new();
    b.extend_from_slice(b"MV7");
    b.push(1);
    b.extend_from_slice(&1u32.to_le_bytes());
    b.push(31);
    b.extend_from_slice(&0u32.to_le_bytes());
    b.extend_from_slice(&0u32.to_le_bytes());
    b.extend_from_slice(&2u32.to_le_bytes());
    for _ in 0..2 {
        b.extend_from_slice(&1u32.to_le_bytes());
        b.extend_from_slice(&0u32.to_le_bytes());
        b.extend_from_slice(&0u32.to_le_bytes());
        b.push(0);
        b.extend_from_slice(&0u32.to_le_bytes());
    }
    b.extend_from_slice(&0u32.to_le_bytes());
    b.extend_from_slice(&0u32.to_le_bytes());
    let mut h: u32 = 0x811c9dc5;
    for &x in &b {
        h ^= x as u32;
        h = h.wrapping_mul(0x01000193);
    }
    b.extend_from_slice(&h.to_le_bytes());
    b
}
fn main() {
    match restore(&duplicate_fiber_bytes()) {
        Ok(_) => print!("OK\n"),
        Err(e) => print!("{}\n", e),
    }
}
