from decimal import Decimal

import pytest
from pydantic import ValidationError

from orderflow.contracts.order import (
    CreateOrderRequest,
    Currency,
)


def test_create_order_request_with_valid_data():
    request = CreateOrderRequest.model_validate(
        {
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
    )

    assert request.customer_id == "cus_123"
    assert request.currency is Currency.USD
    assert len(request.items) == 1
    assert request.items[0].product_id == "prod_1"
    assert request.items[0].quantity == 2
    assert request.items[0].unit_price == Decimal("15.50")


def test_create_order_request_rejects_invalid_currency():
    with pytest.raises(ValidationError):
        CreateOrderRequest.model_validate(
            {
                "customer_id": "cus_123",
                "currency": "BANANA",
                "items": [
                    {
                        "product_id": "prod_1",
                        "quantity": 2,
                        "unit_price": "15.50",
                    }
                ],
            }
        )


def test_create_order_request_requires_at_least_one_item():
    with pytest.raises(ValidationError):
        CreateOrderRequest.model_validate(
            {
                "customer_id": "cus_123",
                "currency": "USD",
                "items": [],
            }
        )


def test_create_order_request_rejects_extra_field():
    with pytest.raises(ValidationError):
        CreateOrderRequest.model_validate(
            {
                "customer_id": "cus_123",
                "currency": "USD",
                "items": [
                    {
                        "product_id": "prod_1",
                        "quantity": 2,
                        "unit_price": "15.50",
                    }
                ],
                "is_admin": True,
            }
        )


def test_create_order_request_rejects_string_quantity():
    with pytest.raises(ValidationError):
        CreateOrderRequest.model_validate(
            {
                "customer_id": "cus_123",
                "currency": "USD",
                "items": [
                    {
                        "product_id": "prod_1",
                        "quantity": "2",
                        "unit_price": "15.50",
                    }
                ],
            }
        )