from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    COP = "COP"


class CreateOrderItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: str = Field(min_length=1)
    quantity: int = Field(gt=0, strict=True)
    unit_price: Decimal = Field(gt=0)


class CreateOrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(min_length=1)
    currency: Currency
    items: list[CreateOrderItemRequest] = Field(min_length=1)
