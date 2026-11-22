#include <iostream>
#include <string>
#include <vector>
#include "gradebook.h"

#ifndef GRADEBOOK_H
#error "gradebook.h is missing or renamed"
#endif

#define CHECK(name, cond) std::cout << "TEST " << #name << " " << ((cond) ? "PASS" : "FAIL") << "\n"

// Compile-time API guard. This function is never called. It exists so that any
// change to the public header or to the Record layout becomes a compile error
// (a real failure) instead of a confusing silent bug.
namespace {
void api_guard() {
    Record r;
    r.name = "n";
    r.score = 0.0;
    r.category = "c";
    std::vector<Record> v;
    std::vector<Record> out;
    add_record(v, r.name, r.score, r.category);
    (void)total_score(v);
    (void)average_score(v);
    (void)count_at_least(v, 0.0);
    (void)count_in_category(v, "c");
    (void)best_student(v);
    (void)worst_student(v);
    list_by_category(v, "c", out);
    filter_passing(v, 0.0, out);
    (void)remove_first(v, "n");
}
}  // namespace

static std::vector<Record> sample() {
    std::vector<Record> v;
    add_record(v, "Alice", 70.0, "exam");
    add_record(v, "Bob", 80.0, "Quiz");
    add_record(v, "Cara", 90.0, "exam");
    return v;
}

int main() {
    // 1. add_record appends one record with all three fields.
    std::vector<Record> added;
    add_record(added, "Dan", 60.0, "hw");
    bool ok_add = (added.size() == 1) && (added[0].name == "Dan") &&
                  (added[0].score == 60.0) && (added[0].category == "hw");
    CHECK(v_add_record, ok_add);

    std::vector<Record> v = sample();

    // 2. total_score = 70 + 80 + 90 = 240.
    double t = total_score(v);
    CHECK(v_total_score, t > 239.9 && t < 240.1);

    // 3. average_score = 240 / 3 = 80.
    double avg = average_score(v);
    CHECK(v_average_basic, avg > 79.9 && avg < 80.1);

    // 4. count_at_least must consider every record, including the last.
    int c = count_at_least(v, 70.0);
    CHECK(v_count_at_least, c == 3);

    // 5. category match ignores letter case: "Quiz" matches "quiz".
    int q = count_in_category(v, "quiz");
    CHECK(v_count_in_category, q == 1);

    // 6. best_student = highest score = Cara.
    std::string b = best_student(v);
    CHECK(v_best_student, b == "Cara");

    // 7. worst_student = lowest score = Alice.
    std::string w = worst_student(v);
    CHECK(v_worst_student, w == "Alice");

    // 8. list_by_category with a separate output vector.
    std::vector<Record> out;
    list_by_category(v, "EXAM", out);
    bool ok_list = (out.size() == 2) && (out[0].name == "Alice") && (out[1].name == "Cara");
    CHECK(v_list_by_category, ok_list);

    // 9. filter_passing keeps score >= threshold, so 80 and 90 both pass.
    std::vector<Record> pass;
    filter_passing(v, 80.0, pass);
    bool ok_filter = (pass.size() == 2) && (pass[0].name == "Bob") && (pass[1].name == "Cara");
    CHECK(v_filter_passing, ok_filter);

    // 10. remove_first removes only the matching record.
    std::vector<Record> r = sample();
    bool removed = remove_first(r, "Bob");
    bool ok_remove = removed && (r.size() == 2) &&
                     (r[0].name == "Alice") && (r[1].name == "Cara");
    CHECK(v_remove_first, ok_remove);

    // 11. average_score must reflect the current vector, not a cached one.
    std::vector<Record> two;
    add_record(two, "P", 0.0, "x");
    add_record(two, "Q", 100.0, "x");
    double avg2 = average_score(two);
    CHECK(v_average_after_add, avg2 > 49.9 && avg2 < 50.1);

    // 12. empty-book edges that do not involve total or average.
    std::vector<Record> e;
    std::string eb = best_student(e);
    std::string ew = worst_student(e);
    int ec = count_at_least(e, 50.0);
    CHECK(v_empty_book, eb.empty() && ew.empty() && ec == 0);

    return 0;
}
