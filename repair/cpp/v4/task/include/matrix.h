#ifndef STRATA_MATRIX_H
#define STRATA_MATRIX_H

#include <cstddef>
#include <string>

// A dense matrix of doubles stored in row-major order. Storage is an array of
// row pointers; each row is a separate allocation. Indexing is zero-based.
class Matrix {
public:
    Matrix();
    Matrix(std::size_t rows, std::size_t cols);
    Matrix(const Matrix& other);
    Matrix& operator=(const Matrix& other);
    ~Matrix();

    std::size_t rows() const;
    std::size_t cols() const;

    double& at(std::size_t r, std::size_t c);
    const double& at(std::size_t r, std::size_t c) const;
    const double* row(std::size_t r) const;
    void fill(double value);

    Matrix multiply(const Matrix& rhs) const;
    Matrix add(const Matrix& rhs) const;
    Matrix transpose() const;

private:
    std::size_t nrows_;
    std::size_t ncols_;
    double** data_;
};

// A row reduction consumes a contiguous row and returns one number.
typedef double (*RowReduce)(const double* row, std::size_t n);

// A binary reduction consumes an accumulated value and the next element.
typedef double (*BinaryReduce)(double acc, double value);

double reduce_all(const Matrix& m, RowReduce op);
double fold_all(const Matrix& m, BinaryReduce op, double init);

double sum_row(const double* row, std::size_t n);
double max_row(const double* row, std::size_t n);
double min_row(const double* row, std::size_t n);
double product_row(const double* row, std::size_t n);

double add_op(double acc, double value);
double sub_op(double acc, double value);
double mul_op(double acc, double value);

std::string format_matrix(const Matrix& m);

#endif
