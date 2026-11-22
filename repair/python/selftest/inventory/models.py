"""Domain types for the inventory service."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    sku: str
    name: str
    category: str
    price_cents: int
    quantity: int = 1

    @property
    def value_cents(self) -> int:
        return self.price_cents * self.quantity
