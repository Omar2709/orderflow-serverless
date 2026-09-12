import json
from pathlib import Path
from uuid import UUID

from orderflow.handlers.create_order import create_order, lambda_handler

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def load_event():
    fixture = FIXTURES_DIR / "api_gateway_create_order.json"
    return json.loads(fixture.read_text())


def test_create_order_with_valid_body():
    event = load_event()

    response = lambda_handler(event, None)

    assert response["statusCode"] == 201

    body = json.loads(response["body"])

    assert body["customer_id"] == "cus_123"
    assert body["currency"] == "USD"
    assert body["status"] == "PENDING"
    assert body["total"] == "31.00"
    assert body["order_id"]


def test_create_order_with_empty_body():
    event = load_event()
    event["body"] = ""

    response = lambda_handler(event, None)

    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body == {
        "error": "request body is required",
    }


def test_create_order_with_invalid_json():
    event = load_event()
    event["body"] = '{"customer_id": "cus_123"'

    response = lambda_handler(event, None)

    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body == {
        "error": "invalid JSON",
    }


def test_create_order_with_incomplete_request():
    event = load_event()

    event["body"] = json.dumps(
        {
            "customer_id": "cus_123",
            "items": [
                {
                    "product_id": "prod_1",
                    "quantity": 2,
                    "unit_price": "15.50",
                }
            ],
        }
    )

    response = lambda_handler(event, None)

    assert response["statusCode"] == 422

    body = json.loads(response["body"])

    assert body["error"] == "validation error"
    assert body["details"][0]["loc"] == ["currency"]
    assert body["details"][0]["type"] == "missing"


def test_create_order_with_invalid_currency():
    event = load_event()

    event["body"] = json.dumps(
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

    response = lambda_handler(event, None)

    assert response["statusCode"] == 422

    body = json.loads(response["body"])

    assert body["error"] == "validation error"
    assert body["details"][0]["loc"] == ["currency"]


def test_create_order_with_empty_items():
    event = load_event()

    event["body"] = json.dumps(
        {
            "customer_id": "cus_123",
            "currency": "USD",
            "items": [],
        }
    )

    response = lambda_handler(event, None)

    assert response["statusCode"] == 422

    body = json.loads(response["body"])

    assert body["error"] == "validation error"
    assert body["details"][0]["loc"] == ["items"]


def test_create_order_with_negative_quantity():
    event = load_event()

    event["body"] = json.dumps(
        {
            "customer_id": "cus_123",
            "currency": "USD",
            "items": [
                {
                    "product_id": "prod_1",
                    "quantity": -2,
                    "unit_price": "15.50",
                }
            ],
        }
    )

    response = lambda_handler(event, None)

    assert response["statusCode"] == 422

    body = json.loads(response["body"])

    assert body["error"] == "validation error"
    assert body["details"][0]["loc"] == ["items", 0, "quantity"]


def test_create_order_rejects_extra_fields():
    event = load_event()

    event["body"] = json.dumps(
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

    response = lambda_handler(event, None)

    assert response["statusCode"] == 422

    body = json.loads(response["body"])

    assert body["error"] == "validation error"
    assert body["details"][0]["loc"] == ["is_admin"]
    assert body["details"][0]["type"] == "extra_forbidden"


def test_create_order_rejects_string_quantity():
    event = load_event()

    event["body"] = json.dumps(
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

    response = lambda_handler(event, None)

    assert response["statusCode"] == 422

    body = json.loads(response["body"])

    assert body["error"] == "validation error"
    assert body["details"][0]["loc"] == ["items", 0, "quantity"]
    assert body["details"][0]["type"] == "int_type"


def test_create_order_rejects_negative_unit_price():
    event = load_event()

    event["body"] = json.dumps(
        {
            "customer_id": "cus_123",
            "currency": "USD",
            "items": [
                {
                    "product_id": "prod_1",
                    "quantity": 2,
                    "unit_price": "-15.50",
                }
            ],
        }
    )

    response = lambda_handler(event, None)

    assert response["statusCode"] == 422

    body = json.loads(response["body"])

    assert body["error"] == "validation error"
    assert body["details"][0]["loc"] == [
        "items",
        0,
        "unit_price",
    ]
    assert body["details"][0]["type"] == "greater_than"


def test_create_order_preserves_correlation_id():
    event = load_event()

    event["headers"]["x-correlation-id"] = "test-correlation-123"

    response = lambda_handler(event, None)

    assert response["statusCode"] == 201
    assert response["headers"]["x-correlation-id"] == "test-correlation-123"


def test_create_order_generates_correlation_id():
    event = load_event()

    event["headers"].pop("x-correlation-id", None)

    response = lambda_handler(event, None)

    assert response["statusCode"] == 201

    correlation_id = response["headers"]["x-correlation-id"]

    assert correlation_id

    UUID(correlation_id)


def test_validation_error_preserves_correlation_id():
    event = load_event()

    event["headers"]["x-correlation-id"] = "validation-test"
    event["body"] = "{}"

    response = lambda_handler(event, None)

    assert response["statusCode"] == 422
    assert response["headers"]["x-correlation-id"] == "validation-test"


def test_create_order_returns_generic_500_on_unexpected_error(
    monkeypatch,
):
    event = load_event()

    event["headers"]["x-correlation-id"] = "error-test"

    def raise_unexpected_error(_data):
        raise RuntimeError("database exploded")

    monkeypatch.setattr(
        create_order,
        "execute",
        raise_unexpected_error,
    )

    response = lambda_handler(event, None)

    assert response["statusCode"] == 500
    assert response["headers"]["x-correlation-id"] == "error-test"

    body = json.loads(response["body"])

    assert body == {
        "error": "internal server error",
    }

    assert "database exploded" not in response["body"]
