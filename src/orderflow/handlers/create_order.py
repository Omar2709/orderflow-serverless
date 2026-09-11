import json

from pydantic import ValidationError

from orderflow.application.create_order import CreateOrder
from orderflow.contracts.order import CreateOrderRequest
from orderflow.domain.order import Order

create_order = CreateOrder()


def lambda_handler(event, context):
    raw_body = event.get("body")

    if not raw_body:
        return _response(
            400,
            {"error": "request body is required"},
        )

    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError:
        return _response(
            400,
            {"error": "invalid JSON"},
        )

    try:
        request = CreateOrderRequest.model_validate(data)
    except ValidationError as exc:
        return _response(
            400,
            {
                "error": "validation error",
                "details": exc.errors(include_url=False),
            },
        )

    order = create_order.execute(
        request.model_dump(mode="json")
    )

    return _response(
        201,
        _order_to_dict(order),
    )


def _order_to_dict(order: Order) -> dict:
    return {
        "order_id": order.order_id,
        "customer_id": order.customer_id,
        "currency": order.currency,
        "status": order.status,
        "total": str(order.total),
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": str(item.unit_price),
            }
            for item in order.items
        ],
    }


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
        },
        "body": json.dumps(body),
    }