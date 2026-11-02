
"""MiniPay transaction investigation support tool.

Usage:
    python python/support_tool.py --transaction TXN000001
    python python/support_tool.py --transaction TXN000001 --json

Requires DATABASE_URL to be configured in the environment.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def get_transaction(engine, transaction_ref):
    """Retrieve transaction, customer, and callback information."""

    with engine.connect() as connection:
        transaction = connection.execute(
            text(
                """
                SELECT
                    t.id,
                    t.transaction_ref,
                    t.amount,
                    t.status,
                    t.created_at,
                    t.completed_at,
                    t.failure_code,
                    c.id AS customer_id,
                    c.customer_ref,
                    c.name AS customer_name
                FROM transactions t
                JOIN customers c ON c.id = t.customer_id
                WHERE t.transaction_ref = :transaction_ref
                ORDER BY t.id DESC
                LIMIT 1
                """
            ),
            {"transaction_ref": transaction_ref},
        ).mappings().first()

        if transaction is None:
            return None

        callbacks = connection.execute(
            text(
                """
                SELECT
                    attempt_no,
                    http_status,
                    callback_status,
                    attempted_at
                FROM callbacks
                WHERE transaction_id = :transaction_id
                ORDER BY attempt_no
                """
            ),
            {"transaction_id": transaction["id"]},
        ).mappings().all()

    return {
        "transaction": dict(transaction),
        "callbacks": [dict(callback) for callback in callbacks],
    }


def analyze_transaction(result):
    """Identify transaction anomalies and suggest a next action."""

    transaction = result["transaction"]
    callbacks = result["callbacks"]

    anomalies = []
    recommendations = []

    if transaction["status"] == "PROCESSING":
        created_at = transaction["created_at"]

        if created_at.tzinfo is None:
            now = datetime.now()
        else:
            now = datetime.now(timezone.utc)

        age_minutes = (now - created_at).total_seconds() / 60

        if age_minutes > 15:
            anomalies.append(
                f"Transaction has remained PROCESSING for "
                f"{age_minutes:.1f} minutes."
            )
            recommendations.append(
                "Check upstream operator status and investigate why "
                "the transaction has not reached a final state."
            )
        else:
            recommendations.append(
                "Monitor the transaction until it reaches a final state."
            )

    elif transaction["status"] == "FAILED":
        anomalies.append(
            f"Transaction failed with code: "
            f"{transaction['failure_code'] or 'Not provided'}."
        )
        recommendations.append(
            "Review application and upstream logs using the transaction "
            "reference and failure code."
        )

    callback_failures = [
        callback for callback in callbacks
        if callback["callback_status"] == "FAILED"
    ]

    callback_successes = [
        callback for callback in callbacks
        if callback["callback_status"] == "SUCCESS"
    ]

    if callback_failures:
        anomalies.append(
            f"{len(callback_failures)} callback attempt(s) failed."
        )
        recommendations.append(
            "Check merchant callback endpoint availability, HTTP responses, "
            "and retry history."
        )

    if transaction["status"] == "SUCCESS" and not callback_successes:
        anomalies.append(
            "Transaction is SUCCESS but no successful callback was recorded."
        )
        recommendations.append(
            "Verify callback delivery and reconcile the merchant's "
            "transaction status."
        )

    if not anomalies:
        anomalies.append("No obvious anomaly detected in the available records.")
        recommendations.append(
            "No immediate action indicated. Continue normal monitoring."
        )

    return {
        "anomalies": anomalies,
        "recommended_actions": recommendations,
    }


def json_safe(value):
    """Convert database values into JSON-compatible values."""

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    raise TypeError(f"Unsupported JSON value: {type(value).__name__}")


def main():
    parser = argparse.ArgumentParser(
        description="Investigate a MiniPay transaction."
    )
    parser.add_argument(
        "--transaction",
        required=True,
        help="Transaction reference, for example TXN000001",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the investigation result as JSON.",
    )

    args = parser.parse_args()

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print(
            "ERROR: DATABASE_URL environment variable is not configured.",
            file=sys.stderr,
        )
        return 3

    try:
        engine = create_engine(database_url, pool_pre_ping=True)

        try:
            result = get_transaction(engine, args.transaction)
        finally:
            engine.dispose()

    except SQLAlchemyError as error:
        print(f"ERROR: Database operation failed: {error}", file=sys.stderr)
        return 3

    if result is None:
        print(
            f"Transaction not found: {args.transaction}",
            file=sys.stderr,
        )
        return 2

    analysis = analyze_transaction(result)

    report = {
        "transaction": result["transaction"],
        "callbacks": result["callbacks"],
        **analysis,
    }

    if args.json:
        print(json.dumps(report, default=json_safe, indent=2))
    else:
        transaction = report["transaction"]

        print("MINIPAY TRANSACTION INVESTIGATION")
        print("--------------------------------")
        print(f"Transaction ID : {transaction['id']}")
        print(f"Reference      : {transaction['transaction_ref']}")
        print(f"Customer       : {transaction['customer_name']}")
        print(f"Customer Ref   : {transaction['customer_ref']}")
        print(f"Customer ID    : {transaction['customer_id']}")
        print(f"Amount         : {transaction['amount']}")
        print(f"Status         : {transaction['status']}")
        print(f"Created At     : {transaction['created_at']}")
        print(f"Completed At   : {transaction['completed_at']}")
        print(f"Failure Code   : {transaction['failure_code']}")

        print("\nCALLBACK HISTORY")
        print("----------------")
        if not report["callbacks"]:
            print("No callback attempts recorded.")
        else:
            for callback in report["callbacks"]:
                print(
                    f"Attempt {callback['attempt_no']}: "
                    f"HTTP {callback['http_status']} | "
                    f"{callback['callback_status']} | "
                    f"{callback['attempted_at']}"
                )

        print("\nANOMALIES")
        print("---------")
        for anomaly in report["anomalies"]:
            print(f"- {anomaly}")

        print("\nRECOMMENDED ACTIONS")
        print("-------------------")
        for action in report["recommended_actions"]:
            print(f"- {action}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
