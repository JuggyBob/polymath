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
    safe("h_sum_empty", || sum(&[]) == 0);
    safe("h_sum_negative", || sum(&[-5, 10, -3]) == 2);

    let mixed = [black_box(i32::MAX), black_box(i32::MAX), black_box(-1i32)];
    safe("h_sum_large_mixed", || sum(&mixed) == 4_294_967_293i64);

    safe("h_max_single", || max(&[7]) == Some(7));
    safe("h_max_negative", || max(&[-3, -1, -7]) == Some(-1));
    safe("h_max_empty", || max(&[]) == None);

    safe("h_average_fraction", || average(&[1, 2]) == Some(1.5));
    safe("h_average_negative", || average(&[-3, -6]) == Some(-4.5));
    safe("h_average_single", || average(&[7]) == Some(7.0));

    safe("h_count_mixed", || count_matching(&[1, 2, 3], 2) == 1);
    safe("h_count_all", || count_matching(&[2, 2, 2], 2) == 3);

    safe("h_unique_mixed", || {
        unique_sorted(&[2, 1, 2, 1, 3]) == vec![1, 2, 3]
    });
    safe("h_unique_empty", || unique_sorted(&[]).is_empty());

    safe("h_chunk_exact", || {
        chunk(&[1, 2, 3, 4], 2) == vec![vec![1, 2], vec![3, 4]]
    });
    safe("h_chunk_partial", || {
        chunk(&[1, 2, 3, 4, 5], 3) == vec![vec![1, 2, 3], vec![4, 5]]
    });

    safe("h_clamp_low", || clamp(-1, -5, 5) == -1);

    safe("h_word_count_unicode", || word_count("α β\tc") == 3);
    safe("h_char_count_unicode", || char_count("日本語 abc") == 7);
}
