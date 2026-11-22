#include "stats.h"

int max_temp(const int values[], int n) {
    int best = values[0];
    for (int i = 1; i < n; i++) {
        if (values[i] > best) best = values[i];
    }
    return best;
}

int min_temp(const int values[], int n) {
    int best = values[0];
    for (int i = 1; i < n; i++) {
        if (values[i] < best) best = values[i];
    }
    return best;
}

double average_temp(const int values[], int n) {
    int total = 0;
    for (int i = 0; i < n; i++) total += values[i];
    return (double)total / n;
}

int count_above(const int values[], int n, int threshold) {
    int count = 0;
    for (int i = 0; i < n; i++) {
        if (values[i] > threshold) count++;
    }
    return count;
}

int day_of_min(const int values[], int n) {
    int best = values[0];
    int index = 0;
    for (int i = 1; i < n; i++) {
        if (values[i] < best) {
            best = values[i];
            index = i;
        }
    }
    return index + 1;
}

bool valid_range(int value, int lo, int hi) {
    return value >= lo && value <= hi;
}

void swap_values(int& a, int& b) {
    int tmp = a;
    a = b;
    b = tmp;
}

int sum_even(const int values[], int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        if (values[i] % 2 == 0) total += values[i];
    }
    return total;
}

void sort_ascending(int values[], int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - 1 - i; j++) {
            if (values[j] > values[j + 1]) {
                swap_values(values[j], values[j + 1]);
            }
        }
    }
}

int count_duplicates(const int values[], int n) {
    int count = 0;
    for (int i = 0; i < n; i++) {
        bool seen = false;
        for (int j = 0; j < i; j++) {
            if (values[j] == values[i]) { seen = true; break; }
        }
        if (seen) continue;
        int dups = 0;
        for (int j = i + 1; j < n; j++) {
            if (values[j] == values[i]) dups++;
        }
        if (dups > 0) count++;
    }
    return count;
}
