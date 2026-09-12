import json
from uuid import uuid4

from pydantic import ValidationError

from orderflow.application.create_order import CreateOrder
from orderflow.contracts.order import CreateOrderRequest
from orderflow.domain.order import Order

create_order = CreateOrder()


def lambda_handler(event, context):
    correlation_id = _get_correlation_id(event)

    raw_body = event.get("body")

    if not raw_body:
        return _response(
            400,
            {"error": "request body is required"},
            correlation_id,
        )

    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError:
        return _response(
            400,
            {"error": "invalid JSON"},
            correlation_id,
        )

    try:
        request = CreateOrderRequest.model_validate(data)

        order = create_order.execute(request.model_dump(mode="json"))

    except ValidationError as exc:
        return _response(
            422,
            {
                "error": "validation error",
                "details": _validation_errors(exc),
            },
            correlation_id,
        )

    except Exception:  # noqa: BLE001
        return _response(
            500,
            {"error": "internal server error"},
            correlation_id,
        )

    return _response(
        201,
        _order_to_dict(order),
        correlation_id,
    )


def _get_correlation_id(event: dict) -> str:
    headers = event.get("headers") or {}

    correlation_id = headers.get("x-correlation-id")

    if correlation_id:
        return correlation_id

    return str(uuid4())


def _validation_errors(exc: ValidationError) -> list[dict]:
    return [
        {
            "type": error["type"],
            "loc": list(error["loc"]),
            "msg": error["msg"],
        }
        for error in exc.errors(include_url=False)
    ]


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


def _response(
    status_code: int,
    body: dict,
    correlation_id: str,
) -> dict:
    return {
        "statusCode": status_code,
        "headers": {
            "content-type": "application/json",
            "x-correlation-id": correlation_id,
        },
        "body": json.dumps(body),
    }
