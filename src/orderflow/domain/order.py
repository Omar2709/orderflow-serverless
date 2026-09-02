from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OrderItem:
    product_id: str
    quantity: int
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass(frozen=True)
class Order:
    order_id: str
    customer_id: str
    currency: str
    items: tuple[OrderItem, ...]
    status: str

    @property
    def total(self) -> Decimal:
        return sum(
            (item.subtotal for item in self.items),
            start=Decimal("0.00"),
        )