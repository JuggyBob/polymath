#![allow(dead_code)]

use std::cell::UnsafeCell;
use std::mem::MaybeUninit;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};

// ---------------------------------------------------------------------------
// A raw-pointer owned buffer.
// ---------------------------------------------------------------------------

pub struct RawVec {
    ptr: *mut i32,
    len: usize,
    cap: usize,
}

unsafe impl Send for RawVec {}
unsafe impl Sync for RawVec {}

impl RawVec {
    pub fn new() -> Self {
        RawVec { ptr: std::ptr::null_mut(), len: 0, cap: 0 }
    }

    pub fn with_capacity(cap: usize) -> Self {
        let mut v = Vec::<i32>::with_capacity(cap);
        let p = v.as_mut_ptr();
        std::mem::forget(v);
        RawVec { ptr: p, len: 0, cap }
    }

    fn reserve(&mut self) {
        let new_cap = if self.cap == 0 { 4 } else { self.cap * 2 };
        let mut nv = Vec::<i32>::with_capacity(new_cap);
        unsafe {
            if self.len > 0 {
                std::ptr::copy_nonoverlapping(self.ptr, nv.as_mut_ptr(), self.len);
            }
        }
        let new_ptr = nv.as_mut_ptr();
        std::mem::forget(nv);
        if self.cap > 0 {
            unsafe { drop(Vec::from_raw_parts(self.ptr, self.len, self.cap)); }
        }
        self.ptr = new_ptr;
        self.cap = new_cap;
    }

    pub fn push(&mut self, x: i32) {
        if self.len == self.cap { self.reserve(); }
        unsafe { std::ptr::write(self.ptr.add(self.len), x); }
        self.len += 1;
    }

    pub fn len(&self) -> usize { self.len }

    pub fn cap(&self) -> usize { self.cap }

    pub fn get(&self, i: usize) -> Option<i32> {
        if i < self.len {
            Some(unsafe { std::ptr::read(self.ptr.add(i)) })
        } else {
            None
        }
    }

    pub fn first(&self) -> Option<i32> { self.get(0) }

    pub fn as_slice(&self) -> &[i32] {
        if self.len == 0 {
            &[]
        } else {
            unsafe { std::slice::from_raw_parts(self.ptr, self.len) }
        }
    }

    /// Sum of all initialized elements.
    pub fn sum(&self) -> i32 {
        self.as_slice().iter().sum()
    }

    /// Remove and return the last element.
    pub fn pop(&mut self) -> Option<i32> {
        if self.len == 0 { return None; }
        self.len -= 1;
        Some(unsafe { std::ptr::read(self.ptr.add(self.len)) })
    }

    /// Whether `x` occurs anywhere in the buffer.
    pub fn contains(&self, x: &i32) -> bool {
        self.as_slice().contains(x)
    }

    /// Reverse all elements in place.
    pub fn reverse(&mut self) {
        if self.len < 2 { return; }
        let s = unsafe { std::slice::from_raw_parts_mut(self.ptr, self.len) };
        s.reverse();
    }

    pub fn clear(&mut self) { self.len = 0; }
}

impl Drop for RawVec {
    fn drop(&mut self) {
        if self.cap > 0 {
            unsafe { drop(Vec::from_raw_parts(self.ptr, self.len, self.cap)); }
        }
    }
}

// ---------------------------------------------------------------------------
// Shared state behind Arc<Mutex<_>>.
// ---------------------------------------------------------------------------

#[derive(Clone)]
pub struct SharedCounter {
    inner: Arc<Mutex<i64>>,
}

impl SharedCounter {
    pub fn new() -> Self {
        SharedCounter { inner: Arc::new(Mutex::new(0)) }
    }

    pub fn inc(&self) -> bool {
        if let Ok(mut g) = self.inner.lock() { *g += 1; true } else { false }
    }

    pub fn get(&self) -> i64 {
        self.inner.lock().map(|g| *g).unwrap_or(0)
    }

    pub fn set(&self, v: i64) {
        if let Ok(mut g) = self.inner.lock() { *g = v; }
    }

    /// Add `n` and return the value from before the add.
    pub fn fetch_add(&self, n: i64) -> i64 {
        let mut g = self.inner.lock().unwrap();
        let old = *g;
        *g += n;
        old
    }

    /// Set to `new` only when the current value equals `expected`.
    /// Return whether the value changed.
    pub fn compare_set(&self, expected: i64, new: i64) -> bool {
        let mut g = self.inner.lock().unwrap();
        if *g == expected {
            *g = new;
            true
        } else {
            false
        }
    }

    /// Add at most `n`, never exceeding `limit`; return the amount added.
    pub fn add_capped(&self, n: i64, limit: i64) -> i64 {
        let mut g = self.inner.lock().unwrap();
        let remaining = limit - *g;
        let to_add = if remaining < n { remaining } else { n };
        if to_add > 0 {
            *g += to_add;
        }
        to_add
    }

    pub fn strong_count(&self) -> usize { Arc::strong_count(&self.inner) }
}

// ---------------------------------------------------------------------------
// A cell with explicit Send/Sync markers.
// ---------------------------------------------------------------------------

pub struct Cell<T> {
    inner: UnsafeCell<T>,
}

unsafe impl<T: Send> Sync for Cell<T> {}

impl<T> Cell<T> {
    pub fn new(v: T) -> Self { Cell { inner: UnsafeCell::new(v) } }

    pub fn get(&self) -> &T { unsafe { &*self.inner.get() } }

    pub fn set(&self, v: T) { unsafe { *self.inner.get() = v; } }

    /// Replace the value with `f(old)` and return the old value.
    pub fn replace_with<F: FnOnce(&T) -> T>(&self, f: F) -> T where T: Clone {
        let old: T = self.get().clone();
        let new_value = f(&old);
        unsafe { *self.inner.get() = new_value; }
        old
    }
}

/// Run `f` on `v` in a worker thread and return its result.
pub fn on_thread<T: Send + 'static, R: Send + 'static>(
    v: T,
    f: impl Fn(&T) -> R + Send + 'static,
) -> R {
    std::thread::spawn(move || f(&v)).join().unwrap()
}

// ---------------------------------------------------------------------------
// Manual initialization with MaybeUninit.
// ---------------------------------------------------------------------------

pub struct Slot<T> {
    mem: MaybeUninit<T>,
    init: bool,
    writes: usize,
}

impl<T> Slot<T> {
    pub fn new() -> Self {
        Slot { mem: MaybeUninit::uninit(), init: false, writes: 0 }
    }

    /// Place `v`, returning the previous value if one was initialized.
    pub fn put(&mut self, v: T) -> Option<T> {
        let old = if self.init {
            Some(unsafe { std::ptr::read(self.mem.as_ptr()) })
        } else {
            None
        };
        self.mem.write(v);
        self.init = true;
        self.writes += 1;
        old
    }

    pub fn get(&self) -> Option<&T> {
        if self.init { Some(unsafe { self.mem.assume_init_ref() }) } else { None }
    }

    /// Move the value out, leaving the slot empty.
    pub fn take(&mut self) -> Option<T> {
        if self.init {
            self.init = false;
            Some(unsafe { std::ptr::read(self.mem.as_ptr()) })
        } else {
            None
        }
    }

    pub fn is_init(&self) -> bool { self.init }

    /// How many values have been written into this slot in total.
    pub fn init_count(&self) -> usize { self.writes }

    /// Store `v` only when the slot is empty; return whether it was stored.
    pub fn put_if_empty(&mut self, v: T) -> bool {
        if self.init { return false; }
        self.mem.write(v);
        self.init = true;
        self.writes += 1;
        true
    }

    /// Reference to the stored value, or `d` when the slot is empty.
    pub fn get_or<'a>(&'a self, d: &'a T) -> &'a T {
        if self.init { unsafe { &*self.mem.as_ptr() } } else { d }
    }
}

impl<T> Drop for Slot<T> {
    fn drop(&mut self) {
        if self.init { unsafe { self.mem.assume_init_drop(); } }
    }
}

// ---------------------------------------------------------------------------
// Borrowed, zero-copy parsing. Returned strings point into the input.
// ---------------------------------------------------------------------------

/// Split on commas. Empty fields are preserved, in order.
pub fn split_fields(buf: &str) -> Vec<&str> {
    buf.split(',').collect()
}

/// Parse `key=value&key=value`. Pairs with an empty value are preserved.
pub fn parse_pairs(buf: &str) -> Vec<(&str, &str)> {
    buf.split('&')
        .filter_map(|p| p.split_once('='))
        .collect()
}

/// The first comma-separated field of `buf`.
pub fn first_field(buf: &str) -> &str {
    buf.split(',').next().unwrap_or("")
}

/// Parse the `idx`-th comma-separated field as an integer.
pub fn parse_int_field(buf: &str, idx: usize) -> Option<i32> {
    buf.split(',').nth(idx).and_then(|s| s.trim().parse::<i32>().ok())
}

// ---------------------------------------------------------------------------
// Linear-work prefix sum with an instrumented work counter.
// ---------------------------------------------------------------------------

pub static WORK: AtomicUsize = AtomicUsize::new(0);

pub fn work() -> usize { WORK.load(Ordering::Relaxed) }

pub fn reset_work() { WORK.store(0, Ordering::Relaxed) }

/// Sum the first `n` values of `xs`. Contract: O(n) work, i.e. at most 2n
/// increments of the work counter (one bookkeeping step per element allowed).
pub fn prefix_sum(xs: &[i32], n: usize) -> i64 {
    let n = n.min(xs.len());
    let mut total = 0i64;
    for i in 0..n {
        WORK.fetch_add(1, Ordering::Relaxed);
        total += xs[i] as i64;
    }
    total
}

// ---------------------------------------------------------------------------
// Intentional legacy behaviour. Do not change the error policy.
// ---------------------------------------------------------------------------

/// Legacy lenient decoder: malformed input maps to 0. Callers rely on this.
pub fn legacy_decode(s: &str) -> i32 {
    s.parse::<i32>().unwrap_or(0)
}
