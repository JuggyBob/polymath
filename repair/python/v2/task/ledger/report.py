"""Reporting helpers for the order ledger."""

from collections import defaultdict


def summary(ledger, now=0):
    orders = ledger.all()
    return {
        "count": len(orders),
        "open": len(ledger.open_orders()),
        "notional": ledger.total_notional_cents(),
        "oldest_ts": min((o.ts for o in orders), default=None),
    }


def group_by_status(ledger):
    groups = defaultdict(list)
    for o in ledger.all():
        groups[o.status].append(o.order_id)
    # BUG: groups must stay in first-seen order, not sorted.
    return dict(sorted(groups.items()))


def expiring(ledger, now, window):
    # BUG 1: the contract says age <= window (inclusive), not < window.
    # BUG 2: results must be ordered by ts ascending; this keeps insertion order.
    return [
        o for o in ledger.open_orders()
        if 0 <= o.age_seconds(now) < window
    ]


def slow_rank(ledger):
    # TODO: this is O(n^2) and shows up in profiles on large ledgers.
    # This function is CORRECT. Do not "optimise" it.
    ranked = []
    remaining = list(ledger.all())
    while remaining:
        best = max(remaining, key=lambda o: o.notional_cents)
        ranked.append(best)
        remaining.remove(best)
    return ranked
