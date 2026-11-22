//! Ownership and borrowing basics — repair fixture v1.
//!
//! Public signatures are fixed. Some implementations below are wrong;
//! fix the behaviour without changing the API or the tests.

/// Sum of all values, widened to i64.
pub fn sum(values: &[i32]) -> i64 {
    let mut total: i64 = 0;
    for &v in values {
        total += v as i64;
    }
    total
}

/// Largest value, or None for an empty slice.
pub fn max(values: &[i64]) -> Option<i64> {
    if values.is_empty() {
        return None;
    }
    let first = values[0];
    let best = values.iter().copied().max().unwrap();
    Some(if best > first { best } else { first })
}

/// Arithmetic mean, or None for an empty slice.
pub fn average(values: &[i64]) -> Option<f64> {
    if values.is_empty() {
        return None;
    }
    let total: f64 = values.iter().map(|&v| v as f64).sum();
    let n = values.len() as f64;
    Some(total / n)
}

/// Number of values exactly equal to target.
pub fn count_matching(values: &[i64], target: i64) -> usize {
    values.iter().filter(|&&v| v == target).count()
}

/// Sorted, duplicate-free copy of the input.
pub fn unique_sorted(values: &[i64]) -> Vec<i64> {
    let mut v = values.to_vec();
    v.sort_unstable();
    v.dedup();
    v
}

/// Consecutive chunks of `size`; last chunk may be shorter.
pub fn chunk(values: &[i64], size: usize) -> Vec<Vec<i64>> {
    if size == 0 {
        return Vec::new();
    }
    values.chunks(size).map(|c| c.to_vec()).collect()
}

/// Clamp value into the inclusive range [lo, hi]. Assumes lo <= hi.
pub fn clamp(value: i64, lo: i64, hi: i64) -> i64 {
    if value < lo {
        lo
    } else if value > hi {
        hi
    } else {
        value
    }
}

/// Number of whitespace-separated words.
pub fn word_count(s: &str) -> usize {
    s.split_whitespace().count()
}

/// Number of characters, not bytes.
pub fn char_count(s: &str) -> usize {
    s.chars().count()
}
