#[path = "../src/lib.rs"]
mod lib;
use lib::*;

fn report(name: &str, ok: bool) {
    println!("TEST {} {}", name, if ok { "PASS" } else { "FAIL" });
}

fn approx(a: f64, b: f64) -> bool { (a - b).abs() < 1e-9 }

fn main() {
    // Bug 1 - longer(): tie-breaking
    report("test_h_longer_tie", longer("xy", "ab") == "xy");
    report("test_h_longer_obvious", longer("a", "bbb") == "bbb");

    // Bug 2 - first_word()
    report("test_h_first_word_spaces", first_word("  foo bar") == "foo");
    report("test_h_first_word_single", first_word("solo") == "solo");

    // Bug 3 - choose()
    report("test_h_choose_prefer_a", choose("abc", "d") == "abc");
    report("test_h_choose_fallback", choose("", "d") == "d");

    // Bug 4 - Slice::sum()
    report("test_h_sum_all", Slice::new(&[10, 20, 30]).sum() == 60);
    report("test_h_sum_empty", Slice::new(&[]).sum() == 0);

    // Bug 5 - Counter::with()
    report("test_h_with_stores", {
        let c = Counter::new();
        c.set(3);
        c.with(|v| v + 1) == 4 && c.get() == 4
    });
    report("test_h_with_return", {
        let c = Counter::new();
        c.set(3);
        c.with(|v| v + 1) == 4
    });

    // Bug 6 - Counter::transfer()
    report("test_h_transfer_clamped", {
        let a = Counter::new();
        let b = Counter::new();
        a.set(2);
        Counter::transfer(&a, &b, 5) == 2 && b.get() == 2
    });
    report("test_h_transfer_exact", {
        let a = Counter::new();
        let b = Counter::new();
        a.set(10);
        Counter::transfer(&a, &b, 3) == 3 && b.get() == 3
    });

    // Bug 7 - Node::parent_name()
    report("test_h_parent_link", {
        let p = Node::new("p");
        let c = Node::new("c");
        Node::add_child(&p, c.clone());
        c.parent_name().as_deref() == Some("p")
    });
    report("test_h_child_count", {
        let p = Node::new("p");
        let c = Node::new("c");
        Node::add_child(&p, c);
        p.child_count() == 1
    });

    // Bug 8 - Node::descendant_count()
    report("test_h_descendants_deep", {
        let r = Node::new("r");
        let a = Node::new("a");
        let b = Node::new("b");
        let c = Node::new("c");
        Node::add_child(&r, a.clone());
        Node::add_child(&a, b.clone());
        Node::add_child(&b, c);
        r.descendant_count() == 3
    });
    report("test_h_descendants_leaf", Node::new("leaf").descendant_count() == 0);

    // Bug 9 - max_by_key()
    report("test_h_max_key", {
        let xs = [("a", 1), ("b", 9), ("c", 4)];
        max_by_key(&xs, |t| t.1) == Some(("b", 9))
    });
    report("test_h_max_key_single", max_by_key(&[1], |x| *x) == Some(1));

    // Bug 10 - Cache::get_or()
    report("test_h_get_or_hit", {
        mut_cache_hit()
    });
    report("test_h_get_or_miss", {
        let c: Cache<&str, i32> = Cache::new();
        c.get_or(&"k", 7) == 7
    });

    // Bug 11 - Rect::area()
    report("test_h_rect_area", Rect { w: 2.0, h: 5.0 }.area() == 10.0);
    report("test_h_circle_area", approx(Circle { r: 2.0 }.area(), 4.0 * std::f64::consts::PI));

    // Bug 12 - describe()
    report("test_h_describe_mixed", {
        let shapes: Vec<Box<dyn Shape>> = vec![Box::new(Rect { w: 1.0, h: 1.0 }), Box::new(Circle { r: 1.0 })];
        describe(&shapes) == "rect,circle"
    });
    report("test_h_describe_empty", describe(&[]) == "");
}

fn mut_cache_hit() -> bool {
    let mut c = Cache::new();
    c.insert("k", 42);
    c.get_or(&"k", 0) == 42
}
