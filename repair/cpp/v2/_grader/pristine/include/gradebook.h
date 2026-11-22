#ifndef GRADEBOOK_H
#define GRADEBOOK_H

#include <string>
#include <vector>

struct Record {
    std::string name;
    double score;
    std::string category;
};

// Appends one record to the end of the gradebook.
void add_record(std::vector<Record>& book, const std::string& name,
                double score, const std::string& category);

// Sum of every score. An empty gradebook has total 0.0.
double total_score(const std::vector<Record>& book);

// Arithmetic mean of every score. An empty gradebook has average 0.0.
// The result must always reflect the CURRENT contents of book.
double average_score(const std::vector<Record>& book);

// Number of records whose score is greater than or equal to threshold.
// Every record is considered, including the last one.
int count_at_least(const std::vector<Record>& book, double threshold);

// Number of records whose category matches 'category' case-insensitively.
// e.g. "Exam", "exam" and "EXAM" all match.
int count_in_category(const std::vector<Record>& book, const std::string& category);

// Name of the record with the highest score.
// Ties go to the record that appears earliest in book. Empty book: "".
std::string best_student(const std::vector<Record>& book);

// Name of the record with the lowest score.
// Ties go to the record that appears earliest in book. Empty book: "".
std::string worst_student(const std::vector<Record>& book);

// Clears out, then appends every record whose category matches 'category'
// case-insensitively, in their original order.
// Must also work when out is the SAME vector as book.
void list_by_category(const std::vector<Record>& book, const std::string& category,
                      std::vector<Record>& out);

// Clears out, then appends every record whose score is >= threshold,
// in their original order.
void filter_passing(const std::vector<Record>& book, double threshold,
                    std::vector<Record>& out);

// Removes the FIRST record whose name equals 'name' exactly (case-sensitive).
// Returns true if a record was removed, false otherwise.
// When nothing is found, book must be unchanged. Other records keep their order.
bool remove_first(std::vector<Record>& book, const std::string& name);

#endif
