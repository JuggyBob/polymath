#include <iostream>
#include "stats.h"

#define CHECK(name, cond) std::cout << "TEST " << #name << " " << ((cond) ? "PASS" : "FAIL") << "\n"

int main() {
    int a[] = {5, 2, 9, 2, 8};
    CHECK(h_average_fraction, average_temp(a, 5) > 5.0 && average_temp(a, 5) < 6.0);

    int neg[] = {-3, -6};
    CHECK(h_average_negative, average_temp(neg, 2) == -4.5);
    int one[] = {7};
    CHECK(h_average_single, average_temp(one, 1) == 7.0);
    CHECK(h_count_above_strict, count_above(a, 5, 9) == 0);

    int small[] = {-1, 0, 1};
    CHECK(h_count_above_negative, count_above(small, 3, 0) == 1);

    int ties[] = {2, 2, 9};
    CHECK(h_day_of_min_two, day_of_min(ties, 3) == 1);
    int first[] = {2, 9, 3};
    CHECK(h_day_of_min_first, day_of_min(first, 3) == 1);
    int last[] = {9, 3, 2};
    CHECK(h_day_of_min_last, day_of_min(last, 3) == 3);

    CHECK(h_range_low, valid_range(1, 1, 10));
    CHECK(h_range_high, valid_range(10, 1, 10));
    CHECK(h_range_below, !valid_range(0, 1, 10));
    CHECK(h_range_inverted, !valid_range(5, 10, 1));

    int evens[] = {-2, -3, 4};
    CHECK(h_sum_even_negative, sum_even(evens, 3) == 2);
    int zeros[] = {0, 1, 0};
    CHECK(h_sum_even_zero, sum_even(zeros, 3) == 0);

    int rev[] = {5, 4, 3, 2, 1};
    sort_ascending(rev, 5);
    CHECK(h_sort_reverse, rev[0] == 1 && rev[4] == 5);
    int dup[] = {2, 1, 2, 1};
    sort_ascending(dup, 4);
    CHECK(h_sort_duplicates, dup[0] == 1 && dup[1] == 1 && dup[2] == 2 && dup[3] == 2);
    int two[] = {2, 1};
    sort_ascending(two, 2);
    CHECK(h_sort_two, two[0] == 1 && two[1] == 2);

    int guarded[] = {3, 1, 2, -999};
    sort_ascending(guarded, 3);
    CHECK(h_sort_no_overrun, guarded[3] == -999 && guarded[0] == 1 && guarded[2] == 3);

    int trip[] = {3, 3, 3};
    CHECK(h_dups_triple, count_duplicates(trip, 3) == 1);
    int none[] = {1, 2, 3};
    CHECK(h_dups_none, count_duplicates(none, 3) == 0);
    int pairs[] = {1, 1, 2, 2, 3, 3};
    CHECK(h_dups_all_distinct_pairs, count_duplicates(pairs, 6) == 3);
    return 0;
}
