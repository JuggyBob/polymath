#include <iostream>
#include <string>
#include <vector>
#include "gradebook.h"

#define CHECK(name, cond) std::cout << "TEST " << #name << " " << ((cond) ? "PASS" : "FAIL") << "\n"

static void add(std::vector<Record>& v, const std::string& n,
                double s, const std::string& c) {
    add_record(v, n, s, c);
}

int main() {
    // 1. Empty total.
    std::vector<Record> empty;
    double te = total_score(empty);
    CHECK(test_h_total_empty, te == 0.0);

    // 2. Single-record total.
    std::vector<Record> one;
    add(one, "S", 55.0, "hw");
    double ts = total_score(one);
    CHECK(test_h_total_single, ts > 54.9 && ts < 55.1);

    // 3. Fractional average (also the first average call in this binary).
    std::vector<Record> frac;
    add(frac, "A", 0.0, "x");
    add(frac, "B", 100.0, "x");
    add(frac, "C", 100.0, "x");
    double af = average_score(frac);
    CHECK(test_h_average_fraction, af > 66.0 && af < 67.0);

    // 4. Single-record count_at_least: the last record must be counted.
    std::vector<Record> single;
    add(single, "Hi", 90.0, "x");
    int cs = count_at_least(single, 80.0);
    CHECK(test_h_count_at_least_single, cs == 1);

    // 5. Threshold above every score.
    int cn = count_at_least(frac, 101.0);
    CHECK(test_h_count_at_least_none, cn == 0);

    // 6. Mixed-case categories all match one query.
    std::vector<Record> cats;
    add(cats, "a", 1.0, "ExAm");
    add(cats, "b", 2.0, "exam");
    add(cats, "c", 3.0, "EXAM");
    add(cats, "d", 4.0, "quiz");
    int cc = count_in_category(cats, "exam");
    CHECK(test_h_count_category_mixed_case, cc == 3);

    // 7. No matching category.
    int cm = count_in_category(cats, "homework");
    CHECK(test_h_count_category_no_match, cm == 0);

    // 8. Best student, tie broken by earliest record.
    std::vector<Record> bt;
    add(bt, "Low", 10.0, "x");
    add(bt, "X", 95.0, "x");
    add(bt, "Y", 95.0, "x");
    std::string bn = best_student(bt);
    CHECK(test_h_best_tie_earliest, bn == "X");

    // 9. Best student in a one-record book.
    std::string bs = best_student(one);
    CHECK(test_h_best_single, bs == "S");

    // 10. Worst student, tie broken by earliest record.
    std::vector<Record> wt;
    add(wt, "Z", 50.0, "x");
    add(wt, "A", 50.0, "x");
    add(wt, "Hi", 99.0, "x");
    std::string wn = worst_student(wt);
    CHECK(test_h_worst_tie_earliest, wn == "Z");

    // 11. Worst student in a one-record book.
    std::string ws = worst_student(one);
    CHECK(test_h_worst_single, ws == "S");

    // 12. list_by_category when out and book are the same vector.
    std::vector<Record> alias;
    add(alias, "E1", 10.0, "exam");
    add(alias, "Q1", 20.0, "quiz");
    add(alias, "E2", 30.0, "EXAM");
    list_by_category(alias, "exam", alias);
    bool ok_alias = (alias.size() == 2) &&
                    (alias[0].name == "E1") && (alias[1].name == "E2");
    CHECK(test_h_list_category_alias, ok_alias);

    // 13. list_by_category preserves original order with a separate output.
    std::vector<Record> ord;
    add(ord, "first", 1.0, "hw");
    add(ord, "second", 2.0, "exam");
    add(ord, "third", 3.0, "hw");
    add(ord, "fourth", 4.0, "exam");
    std::vector<Record> lo;
    list_by_category(ord, "HW", lo);
    bool ok_ord = (lo.size() == 2) &&
                  (lo[0].name == "first") && (lo[1].name == "third");
    CHECK(test_h_list_category_order, ok_ord);

    // 14. A score exactly equal to the threshold is included.
    std::vector<Record> fb;
    add(fb, "low", 59.0, "x");
    add(fb, "edge", 60.0, "x");
    add(fb, "high", 61.0, "x");
    std::vector<Record> fo;
    filter_passing(fb, 60.0, fo);
    bool ok_fb = (fo.size() == 2) &&
                 (fo[0].name == "edge") && (fo[1].name == "high");
    CHECK(test_h_filter_boundary_equal, ok_fb);

    // 15. filter_passing with no matches.
    std::vector<Record> fn;
    filter_passing(fb, 1000.0, fn);
    CHECK(test_h_filter_none, fn.empty());

    // 16. Removing the last record.
    std::vector<Record> rl;
    add(rl, "a", 1.0, "x");
    add(rl, "b", 2.0, "x");
    add(rl, "c", 3.0, "x");
    bool rlr = remove_first(rl, "c");
    bool ok_rl = rlr && (rl.size() == 2) &&
                 (rl[0].name == "a") && (rl[1].name == "b");
    CHECK(test_h_remove_last, ok_rl);

    // 17. Removing a middle record keeps the rest in order.
    std::vector<Record> rm;
    add(rm, "a", 1.0, "x");
    add(rm, "b", 2.0, "x");
    add(rm, "c", 3.0, "x");
    add(rm, "d", 4.0, "x");
    bool rmr = remove_first(rm, "b");
    bool ok_rm = rmr && (rm.size() == 3) &&
                 (rm[0].name == "a") && (rm[1].name == "c") && (rm[2].name == "d");
    CHECK(test_h_remove_middle_preserves_order, ok_rm);

    // 18. Average must be recomputed after the book changes.
    std::vector<Record> mut;
    add(mut, "p", 0.0, "x");
    add(mut, "q", 100.0, "x");
    double am = average_score(mut);
    CHECK(test_h_average_after_mutation, am > 49.9 && am < 50.1);

    return 0;
}
