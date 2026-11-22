"""Reporting helpers."""

from collections import defaultdict


def total_value_cents(items):
    total = 0
    for item in items:
        total += item.value_cents
    return total


def by_category(items):
    totals = defaultdict(int)
    for item in items:
        totals[item.category] += item.value_cents
    return dict(totals)


def slow_rank(items):
    # TODO: this is O(n^2) and shows up in profiles on large stores.
    ranked = []
    remaining = list(items)
    while remaining:
        best = max(remaining, key=lambda item: item.value_cents)
        ranked.append(best)
        remaining.remove(best)
    return ranked
