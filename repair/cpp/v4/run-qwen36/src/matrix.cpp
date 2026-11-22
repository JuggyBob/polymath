#include "matrix.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <stdexcept>

Matrix::Matrix() : nrows_(0), ncols_(0), data_(0) {}

Matrix::Matrix(std::size_t rows, std::size_t cols)
    : nrows_(rows), ncols_(cols), data_(0) {
    data_ = new double*[nrows_];
    for (std::size_t i = 0; i < nrows_; ++i) {
        data_[i] = new double[ncols_];
        for (std::size_t j = 0; j < ncols_; ++j) data_[i][j] = 0.0;
    }
}

// Copying a Matrix: each object owns its own storage.
Matrix::Matrix(const Matrix& other)
    : nrows_(other.nrows_), ncols_(other.ncols_), data_(0) {
    data_ = new double*[nrows_];
    for (std::size_t i = 0; i < nrows_; ++i) {
        data_[i] = new double[ncols_];
        for (std::size_t j = 0; j < ncols_; ++j) data_[i][j] = other.data_[i][j];
    }
}

Matrix& Matrix::operator=(const Matrix& other) {
    if (this == &other) return *this;
    for (std::size_t i = 0; i < nrows_; ++i) delete[] data_[i];
    delete[] data_;
    nrows_ = other.nrows_;
    ncols_ = other.ncols_;
    data_ = new double*[nrows_];
    for (std::size_t i = 0; i < nrows_; ++i) {
        data_[i] = new double[ncols_];
        for (std::size_t j = 0; j < ncols_; ++j) data_[i][j] = other.data_[i][j];
    }
    return *this;
}

Matrix::~Matrix() {
    for (std::size_t i = 0; i < nrows_; ++i) delete[] data_[i];
    delete[] data_;
}

std::size_t Matrix::rows() const { return nrows_; }
std::size_t Matrix::cols() const { return ncols_; }

double& Matrix::at(std::size_t r, std::size_t c) { return data_[r][c]; }
const double& Matrix::at(std::size_t r, std::size_t c) const { return data_[r][c]; }
const double* Matrix::row(std::size_t r) const { return data_[r]; }

void Matrix::fill(double value) {
    for (std::size_t i = 0; i < nrows_; ++i)
        for (std::size_t j = 0; j < ncols_; ++j) data_[i][j] = value;
}

Matrix Matrix::multiply(const Matrix& rhs) const {
    if (ncols_ != rhs.nrows_)
        throw std::invalid_argument("dimension mismatch");

    Matrix result(nrows_, rhs.ncols_);
    for (std::size_t i = 0; i < nrows_; ++i) {
        for (std::size_t j = 0; j < rhs.ncols_; ++j) {
            double acc = 0.0;
            for (std::size_t k = 0; k < ncols_; ++k)
                acc += at(i, k) * rhs.at(k, j);
            result.at(i, j) = acc;
        }
    }
    return result;
}

Matrix Matrix::add(const Matrix& rhs) const {
    if (nrows_ != rhs.nrows_ || ncols_ != rhs.ncols_)
        throw std::invalid_argument("dimension mismatch");
    Matrix result(nrows_, ncols_);
    for (std::size_t i = 0; i < nrows_; ++i)
        for (std::size_t j = 0; j < ncols_; ++j)
            result.at(i, j) = at(i, j) + rhs.at(i, j);
    return result;
}

Matrix Matrix::transpose() const {
    Matrix result(ncols_, nrows_);
    for (std::size_t i = 0; i < nrows_; ++i)
        for (std::size_t j = 0; j < ncols_; ++j)
            result.at(j, i) = at(i, j);
    return result;
}

double reduce_all(const Matrix& m, RowReduce op) {
    double total = 0.0;
    for (std::size_t i = 0; i < m.rows(); ++i)
        total += op(m.row(i), m.cols());
    return total;
}

double fold_all(const Matrix& m, BinaryReduce op, double init) {
    double acc = init;
    for (std::size_t i = 0; i < m.rows(); ++i)
        for (std::size_t j = 0; j < m.cols(); ++j)
            acc = op(acc, m.at(i, j));
    return acc;
}

double sum_row(const double* row, std::size_t n) {
    double acc = 0.0;
    for (std::size_t i = 0; i < n; ++i) acc += row[i];
    return acc;
}

double max_row(const double* row, std::size_t n) {
    double best = row[0];
    for (std::size_t i = 1; i < n; ++i)
        if (row[i] > best) best = row[i];
    return best;
}

double min_row(const double* row, std::size_t n) {
    double best = row[0];
    for (std::size_t i = 1; i < n; ++i)
        if (row[i] < best) best = row[i];
    return best;
}

double product_row(const double* row, std::size_t n) {
    double acc = 1.0;
    for (std::size_t i = 0; i < n; ++i) acc *= row[i];
    return acc;
}

double add_op(double acc, double value) { return acc + value; }
double sub_op(double acc, double value) { return acc - value; }
double mul_op(double acc, double value) { return acc * value; }

// The quadratic-looking pair scan is the reference duplicate check.
bool has_duplicate_row(const Matrix& m) {
    for (std::size_t i = 0; i < m.rows(); ++i) {
        for (std::size_t j = i + 1; j < m.rows(); ++j) {
            bool same = true;
            for (std::size_t k = 0; k < m.cols(); ++k) {
                if (m.at(i, k) != m.at(j, k)) { same = false; break; }
            }
            if (same) return true;
        }
    }
    return false;
}

std::string format_matrix(const Matrix& m) {
    if (m.rows() == 0) return "<empty>";
    std::string out;
    char buf[64];
    for (std::size_t i = 0; i < m.rows(); ++i) {
        out += "[";
        for (std::size_t j = 0; j < m.cols(); ++j) {
            std::snprintf(buf, sizeof(buf), "%.2f", m.at(i, j));
            out += buf;
            if (j + 1 < m.cols()) out += ", ";
        }
        out += "]";
        if (i + 1 < m.rows()) out += "\n";
    }
    return out;
}
