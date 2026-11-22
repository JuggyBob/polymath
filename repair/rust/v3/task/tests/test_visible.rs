#[path = "../src/lib.rs"]
mod lib;
use lib::*;

fn report(name: &str, ok: bool) {
    println!("TEST {} {}", name, if ok { "PASS" } else { "FAIL" });
}

fn approx(a: f64, b: f64) -> bool { (a - b).abs() < 1e-9 }

fn main() {
    // Lifetime-returning helpers
    report("test_longer_tie", longer("ab", "cd") == "ab");
    report("test_longer_clear", longer("a", "bbb") == "bbb");
    report("test_first_word", first_word("hello world") == "hello");
    report("test_slice_sum", Slice::new(&[1, 2, 3, 4]).sum() == 10);
    report("test_slice_largest", Slice::new(&[3, 9, 2]).largest() == 9);
    report("test_choose", choose("x", "y") == "x");

    // Interior mutability
    let c = Counter::new();
    report("test_counter_with", {
        c.set(5);
        c.with(|v| v * 2) == 10 && c.get() == 10
    });
    let c2 = Counter::new();
    c2.inc();
    c2.inc();
    report("test_counter_basic", c2.get() == 2);
    let src = Counter::new();
    let dst = Counter::new();
    report("test_transfer", {
        src.set(5);
        Counter::transfer(&src, &dst, 10) == 5 && dst.get() == 5
    });

    // Rc / Weak tree
    let root = Node::new("root");
    let child = Node::new("leaf");
    Node::add_child(&root, child.clone());
    report("test_parent_name", child.parent_name().as_deref() == Some("root"));
    let grand = Node::new("grand");
    Node::add_child(&child, grand);
    report("test_descendant_count", root.descendant_count() == 2);

    // Generics
    report("test_max_by_key", max_by_key(&[1, 5, 3], |x| *x) == Some(5));
    let mut cache = Cache::new();
    cache.insert("a", 7);
    report("test_cache_get_or", cache.get_or(&"a", 0) == 7);
    report("test_cache_basic", {
        let mut k = Cache::new();
        k.insert(1, 10);
        k.get(&1) == Some(&10) && k.len() == 1 && cache_len(&k) == 1
    });

    // Trait objects
    let shapes: Vec<Box<dyn Shape>> = vec![Box::new(Rect { w: 3.0, h: 4.0 }), Box::new(Circle { r: 1.0 })];
    report("test_total_area", approx(total_area(&shapes), 12.0 + std::f64::consts::PI));
    report("test_describe", describe(&shapes) == "rect,circle");
}
