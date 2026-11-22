"""Domain types for the order ledger."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Order:
    order_id: str
    ts: int
    side: str
    qty: int
    price_cents: int
    status: str = "open"
    note: str = ""

    @property
    def notional_cents(self) -> int:
        return self.qty * self.price_cents

    def age_seconds(self, now: int) -> int:
        return now - self.ts
