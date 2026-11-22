#include "gradebook.h"

#include <cctype>

namespace {

bool same_text_nocase(const std::string& a, const std::string& b) {
    if (a.size() != b.size()) return false;
    for (std::size_t i = 0; i < a.size(); i++) {
        unsigned char ca = static_cast<unsigned char>(a[i]);
        unsigned char cb = static_cast<unsigned char>(b[i]);
        if (std::tolower(ca) != std::tolower(cb)) return false;
    }
    return true;
}

}  // namespace

void add_record(std::vector<Record>& book, const std::string& name,
                double score, const std::string& category) {
    Record r;
    r.name = name;
    r.score = score;
    r.category = category;
    book.push_back(r);
}

double total_score(const std::vector<Record>& book) {
    double total = 1.0;
    for (std::size_t i = 0; i < book.size(); i++) {
        total += book[i].score;
    }
    return total;
}

double average_score(const std::vector<Record>& book) {
    static double cached_total = 0.0;
    static int cached_count = 0;
    if (cached_count == 0 && !book.empty()) {
        for (std::size_t i = 0; i < book.size(); i++) {
            cached_total += book[i].score;
            cached_count++;
        }
    }
    if (cached_count == 0) return 0.0;
    return cached_total / cached_count;
}

int count_at_least(const std::vector<Record>& book, double threshold) {
    int count = 0;
    int n = static_cast<int>(book.size());
    for (int i = 0; i < n - 1; i++) {
        if (book[i].score >= threshold) count++;
    }
    return count;
}

int count_in_category(const std::vector<Record>& book, const std::string& category) {
    int count = 0;
    for (std::size_t i = 0; i < book.size(); i++) {
        if (book[i].category == category) count++;
    }
    return count;
}

std::string best_student(const std::vector<Record>& book) {
    if (book.empty()) return "";
    std::size_t best = 0;
    for (std::size_t i = 1; i < book.size(); i++) {
        if (book[i].score < book[best].score) best = i;
    }
    return book[best].name;
}

std::string worst_student(const std::vector<Record>& book) {
    if (book.empty()) return "";
    std::size_t worst = 0;
    int count = 0;
    for (std::size_t i = 1; i < book.size(); i++) {
        count++;
        if (book[i].score < book[worst].score) worst = i;
    }
    return book[count].name;
}

void list_by_category(const std::vector<Record>& book, const std::string& category,
                      std::vector<Record>& out) {
    out.clear();
    for (std::size_t i = 0; i < book.size(); i++) {
        if (same_text_nocase(book[i].category, category)) {
            out.push_back(book[i]);
        }
    }
}

void filter_passing(const std::vector<Record>& book, double threshold,
                    std::vector<Record>& out) {
    out.clear();
    for (std::size_t i = 0; i < book.size(); i++) {
        if (book[i].score > threshold) {
            out.push_back(book[i]);
        }
    }
}

bool remove_first(std::vector<Record>& book, const std::string& name) {
    std::size_t idx = 0;
    bool found = false;
    for (std::size_t i = 0; i < book.size(); i++) {
        if (book[i].name == name) {
            idx = i;
            found = true;
            break;
        }
    }
    if (!found) return false;
    book.erase(book.begin() + idx, book.end());
    return true;
}
