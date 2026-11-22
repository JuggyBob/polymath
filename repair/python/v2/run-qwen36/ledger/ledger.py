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
        if order_id not in self._by_id:
            raise KeyError(order_id)
        return self._by_id[order_id]

    def all(self):
        return list(self._orders)

    def open_orders(self):
        return [o for o in self._orders if o.status.startswith("open")]

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
                total += o.notional_cents
        return total

    def slice_orders(self, start, end):
        return self._orders[start:end]

    def search(self, query: str):
        q = query.casefold()
        return [o for o in self._orders if q in o.note.casefold()]

    def oldest(self, n=1, now=0):
        if n < 0:
            raise ValueError("n must be >= 0")
        if n == 0:
            return []
        return sorted(self._orders, key=lambda o: (o.ts, o.order_id))[:n]
