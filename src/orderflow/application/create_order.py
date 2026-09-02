from decimal import Decimal
from uuid import uuid4

from orderflow.domain.order import Order, OrderItem


class CreateOrder:
    def execute(self, data: dict) -> Order:
        items = tuple(
            OrderItem(
                product_id=item["product_id"],
                quantity=item["quantity"],
                unit_price=Decimal(item["unit_price"]),
            )
            for item in data["items"]
        )

        return Order(
            order_id=str(uuid4()),
            customer_id=data["customer_id"],
            currency=data["currency"],
            items=items,
            status="PENDING",
        )