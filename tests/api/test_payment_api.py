
"""Integration tests for MiniPay customer and payment APIs."""

from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from application.api.main import app


@pytest.fixture
def client(monkeypatch):
    """Create an authenticated test client."""
    monkeypatch.setenv("MINIPAY_API_KEY", "test-merchant-key")

    with TestClient(
        app,
        headers={"X-API-Key": "test-merchant-key"},
    ) as test_client:
        yield test_client


def create_test_customer(client):
    """Register a customer and return its response data."""
    response = client.post(
        "/api/customers",
        json={
            "customer_ref": f"CUST-{uuid4().hex[:12]}",
            "name": "Test Customer",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_customer(client):
    """Verify successful customer registration."""
    response = client.post(
        "/api/customers",
        json={
            "customer_ref": f"CUST-{uuid4().hex[:12]}",
            "name": "Test Customer",
        },
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Test Customer"
    assert "id" in response.json()


def test_duplicate_customer_reference(client):
    """Verify duplicate customer references are rejected."""
    customer_ref = f"CUST-{uuid4().hex[:12]}"
    payload = {
        "customer_ref": customer_ref,
        "name": "Test Customer",
    }

    first_response = client.post("/api/customers", json=payload)
    second_response = client.post("/api/customers", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_create_payment(client):
    """Verify successful payment submission."""
    customer = create_test_customer(client)

    response = client.post(
        "/api/payments",
        json={
            "transaction_ref": f"TXN-{uuid4().hex[:12]}",
            "customer_id": customer["id"],
            "amount": "1500.50",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "PROCESSING"
    assert Decimal(response.json()["amount"]) == Decimal("1500.50")


def test_payment_with_unknown_customer(client):
    """Verify payment submission fails for an unknown customer."""
    response = client.post(
        "/api/payments",
        json={
            "transaction_ref": f"TXN-{uuid4().hex[:12]}",
            "customer_id": 999999999,
            "amount": "500.00",
        },
    )

    assert response.status_code == 404


def test_duplicate_transaction_reference(client):
    """Verify duplicate transaction references are rejected."""
    customer = create_test_customer(client)
    transaction_ref = f"TXN-{uuid4().hex[:12]}"

    payload = {
        "transaction_ref": transaction_ref,
        "customer_id": customer["id"],
        "amount": "750.00",
    }

    first_response = client.post("/api/payments", json=payload)
    second_response = client.post("/api/payments", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_get_payment(client):
    """Verify retrieval of an existing payment."""
    customer = create_test_customer(client)

    create_response = client.post(
        "/api/payments",
        json={
            "transaction_ref": f"TXN-{uuid4().hex[:12]}",
            "customer_id": customer["id"],
            "amount": "200.00",
        },
    )

    payment_id = create_response.json()["id"]

    response = client.get(f"/api/payments/{payment_id}")

    assert response.status_code == 200
    assert response.json()["id"] == payment_id


def test_get_unknown_payment(client):
    """Verify unknown payment IDs return 404."""
    response = client.get("/api/payments/999999999")

    assert response.status_code == 404


def test_get_customer_payments(client):
    """Verify customer payment history can be retrieved."""
    customer = create_test_customer(client)

    client.post(
        "/api/payments",
        json={
            "transaction_ref": f"TXN-{uuid4().hex[:12]}",
            "customer_id": customer["id"],
            "amount": "300.00",
        },
    )

    response = client.get(
        f"/api/customers/{customer['id']}/payments"
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_invalid_payment_amount(client):
    """Verify zero payment amounts are rejected."""
    customer = create_test_customer(client)

    response = client.post(
        "/api/payments",
        json={
            "transaction_ref": f"TXN-{uuid4().hex[:12]}",
            "customer_id": customer["id"],
            "amount": "0",
        },
    )

    assert response.status_code == 422


def test_payment_rejects_missing_api_key(monkeypatch):
    """Requests without an API key should be rejected."""
    monkeypatch.setenv("MINIPAY_API_KEY", "test-merchant-key")

    with TestClient(app) as unauthenticated_client:
        response = unauthenticated_client.get("/api/payments/1")

    assert response.status_code == 401


def test_payment_rejects_invalid_api_key(monkeypatch):
    """Requests with an incorrect API key should be rejected."""
    monkeypatch.setenv("MINIPAY_API_KEY", "test-merchant-key")

    with TestClient(
        app,
        headers={"X-API-Key": "wrong-key"},
    ) as unauthenticated_client:
        response = unauthenticated_client.get("/api/payments/1")

    assert response.status_code == 401
