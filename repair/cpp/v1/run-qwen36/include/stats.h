#ifndef STATS_H
#define STATS_H

struct Reading {
    int day;
    int temp;
};

int max_temp(const int values[], int n);
int min_temp(const int values[], int n);
double average_temp(const int values[], int n);
int count_above(const int values[], int n, int threshold);
int day_of_min(const int values[], int n);
bool valid_range(int value, int lo, int hi);
void swap_values(int& a, int& b);
int sum_even(const int values[], int n);
void sort_ascending(int values[], int n);
int count_duplicates(const int values[], int n);

#endif
