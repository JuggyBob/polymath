//! Ownership and borrowing basics — repair fixture v1.
//!
//! Public signatures are fixed. Some implementations below are wrong;
//! fix the behaviour without changing the API or the tests.

/// Sum of all values, widened to i64.
pub fn sum(values: &[i32]) -> i64 {
    let mut total: i32 = 0;
    for &v in values {
        // BUG 1: accumulation stays in i32 and wraps for large inputs.
        total = total + v;
    }
    total as i64
}

/// Largest value, or None for an empty slice.
pub fn max(values: &[i64]) -> Option<i64> {
    // BUG 2: direct indexing plus unwrap panics on an empty slice
    // instead of returning None.
    let first = values[0];
    let best = values.iter().copied().max().unwrap();
    Some(if best > first { best } else { first })
}

/// Arithmetic mean, or None for an empty slice.
pub fn average(values: &[i64]) -> Option<f64> {
    if values.is_empty() {
        return None;
    }
    let total: i64 = values.iter().sum();
    let n = values.len() as i64;
    // BUG 3: integer division truncates the fractional part before the cast.
    Some((total / n) as f64)
}

/// Number of values exactly equal to target.
pub fn count_matching(values: &[i64], target: i64) -> usize {
    // BUG 4: >= counts too many values; the contract says ==.
    values.iter().filter(|&&v| v >= target).count()
}

/// Sorted, duplicate-free copy of the input.
pub fn unique_sorted(values: &[i64]) -> Vec<i64> {
    let mut v = values.to_vec();
    // BUG 5: dedup before sort only removes adjacent duplicates.
    v.dedup();
    v.sort_unstable();
    v
}

/// Consecutive chunks of `size`; last chunk may be shorter.
pub fn chunk(values: &[i64], size: usize) -> Vec<Vec<i64>> {
    if size == 0 {
        return Vec::new();
    }
    // BUG 6: chunks of size + 1 are one element too long.
    values.chunks(size + 1).map(|c| c.to_vec()).collect()
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
    // BUG 7: len() counts UTF-8 bytes, not characters.
    s.len()
}
