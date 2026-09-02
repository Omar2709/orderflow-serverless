from decimal import Decimal

from orderflow.application.create_order import CreateOrder


def test_create_order_calculates_total():
    use_case = CreateOrder()

    data = {
        "customer_id": "cus_123",
        "currency": "USD",
        "items": [
            {
                "product_id": "prod_1",
                "quantity": 2,
                "unit_price": "15.50",
            }
        ],
    }

    order = use_case.execute(data)

    assert order.customer_id == "cus_123"
    assert order.currency == "USD"
    assert order.status == "PENDING"
    assert order.total == Decimal("31.00")
    assert order.order_id

def test_create_order_with_multiple_items():
    use_case = CreateOrder()

    data = {
        "customer_id": "cus_123",
        "currency": "USD",
        "items": [
            {
                "product_id": "prod_1",
                "quantity": 2,
                "unit_price": "15.50",
            },
            {
                "product_id": "prod_2",
                "quantity": 3,
                "unit_price": "4.25",
            }
        ],
    }

    order = use_case.execute(data)

    assert order.customer_id == "cus_123"
    assert order.currency == "USD"
    assert order.status == "PENDING"
    assert order.total == Decimal("43.75")
    assert order.order_id