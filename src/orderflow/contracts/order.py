from decimal import Decimal
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

NonBlankStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]


class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    COP = "COP"


class CreateOrderItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: NonBlankStr
    quantity: int = Field(gt=0, strict=True)
    unit_price: Decimal = Field(gt=0)


class CreateOrderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: NonBlankStr
    currency: Currency
    items: list[CreateOrderItemRequest] = Field(min_length=1)
