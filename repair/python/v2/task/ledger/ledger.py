"""In-memory order ledger."""

from .models import Order


class Ledger:
    def __init__(self):
        self._orders = []
        self._by_id = {}

    def add(self, order: Order) -> None:
        if order.order_id in self._by_id:
            raise ValueError(f"duplicate id: {order.order_id}")
        self._orders.append(order)
        self._by_id[order.order_id] = order

    def get(self, order_id: str) -> Order:
        # BUG: should raise KeyError for a missing id.
        return self._by_id.get(order_id)

    def all(self):
        # BUG: should return a copy so callers cannot mutate the ledger.
        return self._orders

    def open_orders(self):
        # BUG: should accept any status that starts with "open".
        return [o for o in self._orders if o.status == "open"]

    def fill(self, order_id: str) -> None:
        order = self._by_id[order_id]
        if order.status == "filled":
            return
        new_order = Order(
            order.order_id, order.ts, order.side, order.qty, order.price_cents,
            "filled", order.note,
        )
        self._by_id[order_id] = new_order
        self._replace(order_id, new_order)

    def cancel(self, order_id: str) -> None:
        order = self._by_id[order_id]
        if order.status == "filled":
            raise ValueError("cannot cancel a filled order")
        new_order = Order(
            order.order_id, order.ts, order.side, order.qty, order.price_cents,
            "cancelled", order.note,
        )
        self._by_id[order_id] = new_order
        self._replace(order_id, new_order)

    def _replace(self, order_id, new_order):
        for i, o in enumerate(self._orders):
            if o.order_id == order_id:
                self._orders[i] = new_order
                return

    def total_notional_cents(self, status=None):
        total = 0
        for o in self._orders:
            if status is None or o.status == status:
                # BUG: should use o.notional_cents (qty * price).
                total += o.price_cents
        return total

    def slice_orders(self, start, end):
        # BUG: end is exclusive; the +1 makes it inclusive and breaks negatives.
        return self._orders[start:end + 1]

    def search(self, query: str):
        # BUG: case folding, not lowercasing.
        return [o for o in self._orders if query.lower() in o.note.lower()]

    def oldest(self, n=1, now=0):
        if n < 0:
            raise ValueError("n must be >= 0")
        if n == 0:
            return []
        # BUG: should be smallest ts first, with order_id as a tie-break.
        return sorted(self._orders, key=lambda o: o.ts, reverse=True)[:n]
