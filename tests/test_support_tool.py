
"""Unit tests for the MiniPay transaction support CLI."""

from datetime import datetime, timedelta
from decimal import Decimal

from python import support_tool


def make_transaction(status="SUCCESS", created_at=None, failure_code=None):
    """Create a sample transaction for testing."""
    return {
        "id": 1,
        "transaction_ref": "TXN000001",
        "amount": Decimal("1500.00"),
        "status": status,
        "created_at": created_at or datetime.now(),
        "completed_at": datetime.now() if status != "PROCESSING" else None,
        "failure_code": failure_code,
        "customer_id": 1,
        "customer_ref": "CUST000001",
        "customer_name": "Test Customer",
    }


def test_successful_transaction_has_no_obvious_anomaly():
    result = {
        "transaction": make_transaction(),
        "callbacks": [
            {
                "attempt_no": 1,
                "http_status": 200,
                "callback_status": "SUCCESS",
                "attempted_at": datetime.now(),
            }
        ],
    }

    analysis = support_tool.analyze_transaction(result)

    assert analysis["anomalies"] == [
        "No obvious anomaly detected in the available records."
    ]


def test_stuck_processing_transaction_is_flagged():
    result = {
        "transaction": make_transaction(
            status="PROCESSING",
            created_at=datetime.now() - timedelta(minutes=30),
        ),
        "callbacks": [],
    }

    analysis = support_tool.analyze_transaction(result)

    assert any(
        "remained PROCESSING" in anomaly
        for anomaly in analysis["anomalies"]
    )


def test_failed_transaction_includes_failure_code():
    result = {
        "transaction": make_transaction(
            status="FAILED",
            failure_code="UPSTREAM_ERROR",
        ),
        "callbacks": [],
    }

    analysis = support_tool.analyze_transaction(result)

    assert any(
        "UPSTREAM_ERROR" in anomaly
        for anomaly in analysis["anomalies"]
    )


def test_successful_transaction_without_successful_callback_is_flagged():
    result = {
        "transaction": make_transaction(),
        "callbacks": [
            {
                "attempt_no": 1,
                "http_status": 500,
                "callback_status": "FAILED",
                "attempted_at": datetime.now(),
            }
        ],
    }

    analysis = support_tool.analyze_transaction(result)

    assert any(
        "no successful callback" in anomaly
        for anomaly in analysis["anomalies"]
    )


def test_json_safe_converts_decimal_and_datetime():
    timestamp = datetime(2026, 9, 1, 12, 0, 0)

    assert support_tool.json_safe(Decimal("125.50")) == "125.50"
    assert support_tool.json_safe(timestamp) == timestamp.isoformat()


def test_cli_requires_database_url(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(
        "sys.argv",
        ["support_tool.py", "--transaction", "TXN000001"],
    )

    assert support_tool.main() == 3
