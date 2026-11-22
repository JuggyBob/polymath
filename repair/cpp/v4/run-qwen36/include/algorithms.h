#ifndef STRATA_ALGORITHMS_H
#define STRATA_ALGORITHMS_H

#include <cstddef>
#include "matrix.h"

// Generic pointer-range algorithms. Explicit instantiations for int and double
// live in algorithms.cpp.
template <typename T> T sum_range(const T* first, const T* last);
template <typename T> T max_range(const T* first, const T* last);
template <typename T> std::size_t count_above_range(const T* first, const T* last, T threshold);

extern template int sum_range<int>(const int*, const int*);
extern template double sum_range<double>(const double*, const double*);
extern template int max_range<int>(const int*, const int*);
extern template double max_range<double>(const double*, const double*);
extern template std::size_t count_above_range<int>(const int*, const int*, int);
extern template std::size_t count_above_range<double>(const double*, const double*, double);

// data points at rows*cols doubles laid out row by row.
double traverse_sum(const double* data, std::size_t rows, std::size_t cols);

// Fills out[0..n) with indices 0..n-1 ordered by value, ties by index.
void sorted_indices(const double* values, std::size_t n, std::size_t* out);

int clamp_count(int requested, std::size_t available);
long long total_of(const int* values, std::size_t n);
bool all_rows_same_sum(const Matrix& m);
double apply_factor(double x);
bool has_duplicate_row(const Matrix& m);

#endif
