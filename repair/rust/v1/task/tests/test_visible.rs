#[path = "../src/lib.rs"]
mod lib;

use lib::*;
use std::hint::black_box;

fn check(name: &str, cond: bool) {
    println!("TEST {} {}", name, if cond {"PASS"} else {"FAIL"});
}

fn safe(name: &str, f: impl FnOnce() -> bool) {
    let cond = std::panic::catch_unwind(std::panic::AssertUnwindSafe(f)).unwrap_or(false);
    check(name, cond);
}

fn main() {
    safe("v_sum_basic", || sum(&[1, 2, 3]) == 6);

    let big = [black_box(2_000_000_000i32), black_box(2_000_000_000i32)];
    safe("v_sum_overflow", || sum(&big) == 4_000_000_000i64);

    safe("v_max_basic", || max(&[3, 1, 2]) == Some(3));
    safe("v_max_empty", || max(&[]) == None);

    safe("v_average_basic", || average(&[1, 2, 3, 4]) == Some(2.5));

    safe("v_count_matching", || count_matching(&[1, 2, 3, 2], 2) == 2);

    safe("v_unique_sorted", || {
        unique_sorted(&[3, 1, 3, 2, 1]) == vec![1, 2, 3]
    });

    safe("v_chunk", || {
        chunk(&[1, 2, 3, 4, 5], 2) == vec![vec![1, 2], vec![3, 4], vec![5]]
    });
    safe("v_chunk_zero", || chunk(&[1, 2], 0).is_empty());

    safe("v_clamp", || {
        clamp(15, 0, 10) == 10 && clamp(-5, 0, 10) == 0 && clamp(5, 0, 10) == 5
    });

    safe("v_word_count", || word_count("  hello\tworld\n") == 2);

    safe("v_char_count", || char_count("héllo") == 5);
}
