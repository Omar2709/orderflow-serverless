import json
from pathlib import Path

from orderflow.handlers.create_order import lambda_handler


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

    event["body"] = json.dumps({
        "customer_id": "cus_123",
        "items": [
            {
                "product_id": "prod_1",
                "quantity": 2,
                "unit_price": "15.50",
            }
        ],
    })

    response = lambda_handler(event, None)

    assert response["statusCode"] == 400

    body = json.loads(response["body"])

    assert body == {
        "error": "missing field: currency",
    }

