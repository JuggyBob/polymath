#include "algorithms.h"

#include <algorithm>

template <typename T>
T sum_range(const T* first, const T* last) {
    T total = static_cast<T>(0);
    for (const T* p = first; p != last; ++p) {
        total += *p;
    }
    return total;
}

template <typename T>
T max_range(const T* first, const T* last) {
    T best = *first;
    for (const T* p = first + 1; p != last; ++p)
        if (*p > best) best = *p;
    return best;
}

template <typename T>
std::size_t count_above_range(const T* first, const T* last, T threshold) {
    std::size_t count = 0;
    for (const T* p = first; p != last; ++p)
        if (*p > threshold) ++count;
    return count;
}

template int sum_range<int>(const int*, const int*);
template double sum_range<double>(const double*, const double*);
template int max_range<int>(const int*, const int*);
template double max_range<double>(const double*, const double*);
template std::size_t count_above_range<int>(const int*, const int*, int);
template std::size_t count_above_range<double>(const double*, const double*, double);

// Walk the buffer in storage order (row by row) — single linear pass.
double traverse_sum(const double* data, std::size_t rows, std::size_t cols) {
    double total = 0.0;
    for (std::size_t i = 0; i < rows * cols; ++i) {
        total += data[i];
    }
    return total;
}

void sorted_indices(const double* values, std::size_t n, std::size_t* out) {
    for (std::size_t i = 0; i < n; ++i) out[i] = i;
    for (std::size_t i = 0; i < n; ++i) {
        for (std::size_t j = i + 1; j < n; ++j) {
            double a = values[out[i]];
            double b = values[out[j]];
            if (b < a || (b == a && out[j] > out[i]))
                std::swap(out[i], out[j]);
        }
    }
}

int clamp_count(int requested, std::size_t available) {
    if (requested < 0) return 0;
    if (requested > static_cast<int>(available)) return static_cast<int>(available);
    return requested;
}

long long total_of(const int* values, std::size_t n) {
    long long acc = 0;
    for (std::size_t i = 0; i < n; ++i) acc += values[i];
    return acc;
}

bool all_rows_same_sum(const Matrix& m) {
    if (m.rows() == 0) return true;
    double first = 0.0;
    for (std::size_t j = 0; j < m.cols(); ++j) first += m.at(0, j);
    for (std::size_t i = 1; i < m.rows(); ++i) {
        double s = 0.0;
        for (std::size_t j = 0; j < m.cols(); ++j) s += m.at(i, j);
        if (s != first) return false;
    }
    return true;
}

double apply_factor(double x) {
    return x * 2.0;
}
