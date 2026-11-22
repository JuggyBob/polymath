#include <iostream>
#include "stats.h"

#define CHECK(name, cond) std::cout << "TEST " << #name << " " << ((cond) ? "PASS" : "FAIL") << "\n"

int main() {
    int a[] = {5, 2, 9, 2, 8};
    CHECK(max_temp, max_temp(a, 5) == 9);
    CHECK(min_temp, min_temp(a, 5) == 2);
    CHECK(average_temp, average_temp(a, 5) == 5.2);
    CHECK(count_above, count_above(a, 5, 5) == 2);
    CHECK(day_of_min, day_of_min(a, 5) == 2);
    CHECK(valid_range_in, valid_range(5, 1, 10));
    CHECK(valid_range_out, !valid_range(11, 1, 10));

    int x = 1, y = 2;
    swap_values(x, y);
    CHECK(swap_values, x == 2 && y == 1);

    CHECK(sum_even, sum_even(a, 5) == 12);

    int b[] = {3, 1, 2};
    sort_ascending(b, 3);
    CHECK(sort_ascending, b[0] == 1 && b[1] == 2 && b[2] == 3);

    int d[] = {3, 3, 4, 4};
    CHECK(count_duplicates, count_duplicates(d, 4) == 2);
    return 0;
}


