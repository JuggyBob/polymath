#![allow(dead_code)]

use std::cell::RefCell;
use std::collections::HashMap;
use std::hash::Hash;
use std::rc::{Rc, Weak};

// ---------------------------------------------------------------------------
// Helpers that return borrowed data
// ---------------------------------------------------------------------------

/// Return the longer of two borrowed strings. Ties resolve to `a`.
pub fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    // # BUG 1: ties must resolve to `a`, but `>` sends them to `b`.
    if a.len() > b.len() { a } else { b }
}

/// Return the first whitespace-delimited word of `s`, borrowed from `s`.
pub fn first_word(s: &str) -> &str {
    // # BUG 2: returns the whole string instead of the first word.
    s
}

/// Choose `a` when it is non-empty, otherwise `b`.
/// Both inputs share one lifetime; the elision is deliberate.
pub fn choose<'a>(a: &'a str, b: &'a str) -> &'a str {
    // # BUG 3: prefers `b` whenever `b` is non-empty, ignoring `a`.
    if b.is_empty() { a } else { b }
}

/// A view over a borrowed slice of integers.
pub struct Slice<'a> {
    data: &'a [i32],
}

impl<'a> Slice<'a> {
    pub fn new(data: &'a [i32]) -> Self { Slice { data } }

    /// Sum of every element in the view.
    pub fn sum(&self) -> i32 {
        // # BUG 4: `saturating_sub(1)` silently drops the final element.
        self.data.iter().take(self.data.len().saturating_sub(1)).sum()
    }

    /// Largest element, or 0 for an empty view.
    pub fn largest(&self) -> i32 {
        self.data.iter().copied().max().unwrap_or(0)
    }

    /// Owned copy of the view.
    pub fn to_vec(&self) -> Vec<i32> { self.data.to_vec() }
}

// ---------------------------------------------------------------------------
// Interior mutability: Rc<RefCell<_>>
// ---------------------------------------------------------------------------

#[derive(Clone)]
pub struct Counter {
    value: Rc<RefCell<i64>>,
}

impl Counter {
    pub fn new() -> Self { Counter { value: Rc::new(RefCell::new(0)) } }

    pub fn inc(&self) { *self.value.borrow_mut() += 1; }

    pub fn add(&self, n: i64) { *self.value.borrow_mut() += n; }

    pub fn get(&self) -> i64 { *self.value.borrow() }

    pub fn set(&self, v: i64) { *self.value.borrow_mut() = v; }

    pub fn strong_count(&self) -> usize { Rc::strong_count(&self.value) }

    /// Apply `f` to the current value and store the result.
    pub fn with<F: FnOnce(i64) -> i64>(&self, f: F) -> i64 {
        let v = *self.value.borrow();
        let out = f(v);
        // # BUG 5: the result of `f` is computed but never written back.
        out
    }

    /// Move `min(n, src)` from `src` into `dst`; return the amount moved.
    pub fn transfer(src: &Counter, dst: &Counter, n: i64) -> i64 {
        let amount = n.min(*src.value.borrow());
        *src.value.borrow_mut() -= amount;
        // # BUG 6: credits `n` instead of the clamped `amount`.
        *dst.value.borrow_mut() += n;
        amount
    }
}

/// A tree node. `parent` is a `Weak` so the tree contains no strong cycle.
pub struct Node {
    pub name: String,
    pub parent: RefCell<Option<Weak<Node>>>,
    pub children: RefCell<Vec<Rc<Node>>>,
}

impl Node {
    pub fn new(name: &str) -> Rc<Self> {
        Rc::new(Node {
            name: name.to_string(),
            parent: RefCell::new(None),
            children: RefCell::new(Vec::new()),
        })
    }

    pub fn add_child(parent: &Rc<Node>, child: Rc<Node>) {
        *child.parent.borrow_mut() = Some(Rc::downgrade(parent));
        parent.children.borrow_mut().push(child);
    }

    /// Name of the parent, if it is still alive.
    pub fn parent_name(&self) -> Option<String> {
        // # BUG 7: reports the node's own name instead of its parent's.
        Some(self.name.clone())
    }

    /// Number of descendants (all levels below this node).
    pub fn descendant_count(&self) -> usize {
        let kids = self.children.borrow();
        // # BUG 8: only direct children are counted.
        kids.len()
    }

    pub fn child_count(&self) -> usize { self.children.borrow().len() }
}

// ---------------------------------------------------------------------------
// Generics
// ---------------------------------------------------------------------------

/// Element with the largest extracted key, or None if empty.
/// The `Clone` bound is intentional and part of the public API.
pub fn max_by_key<T: Clone, K: Ord, F: Fn(&T) -> K>(items: &[T], f: F) -> Option<T> {
    // # BUG 9: uses `min_by_key`, selecting the smallest key.
    items.iter().min_by_key(|t| f(t)).cloned()
}

pub struct Cache<K: Eq + Hash, V> {
    map: HashMap<K, V>,
}

impl<K: Eq + Hash, V> Cache<K, V> {
    pub fn new() -> Self { Cache { map: HashMap::new() } }
    pub fn insert(&mut self, k: K, v: V) -> Option<V> { self.map.insert(k, v) }
    pub fn get(&self, k: &K) -> Option<&V> { self.map.get(k) }
    pub fn len(&self) -> usize { self.map.len() }

    /// Stored value for `k`, or `default` when absent. Requires `V: Clone`.
    pub fn get_or(&self, k: &K, default: V) -> V where V: Clone {
        // # BUG 10: always returns `default`, ignoring a stored value.
        default
    }
}

/// Number of stored values in a cache (free function, no extra bounds).
pub fn cache_len<K: Eq + Hash, V>(c: &Cache<K, V>) -> usize { c.len() }

// ---------------------------------------------------------------------------
// Trait objects
// ---------------------------------------------------------------------------

pub trait Shape {
    fn area(&self) -> f64;
    fn name(&self) -> &'static str;
}

pub struct Rect { pub w: f64, pub h: f64 }
impl Shape for Rect {
    fn area(&self) -> f64 {
        // # BUG 11: adds instead of multiplying.
        self.w + self.h
    }
    fn name(&self) -> &'static str { "rect" }
}

pub struct Circle { pub r: f64 }
impl Shape for Circle {
    fn area(&self) -> f64 { std::f64::consts::PI * self.r * self.r }
    fn name(&self) -> &'static str { "circle" }
}

/// Total area via dynamic dispatch on trait objects.
pub fn total_area(shapes: &[Box<dyn Shape>]) -> f64 {
    shapes.iter().map(|s| s.area()).sum()
}

/// Comma-separated names of the shapes, in order.
pub fn describe(shapes: &[Box<dyn Shape>]) -> String {
    // # BUG 12: hard-codes "rect" for every element.
    shapes.iter().map(|_| "rect").collect::<Vec<_>>().join(",")
}
