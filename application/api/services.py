
"""Business logic for MiniPay customers and payments."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from application.api.models import Customer, Transaction


class CustomerNotFoundError(Exception):
    """Raised when a requested customer does not exist."""


class DuplicateTransactionReferenceError(Exception):
    """Raised when a transaction reference has already been used."""


def create_customer(
    db: Session,
    customer_ref: str,
    name: str,
) -> Customer:
    """Create and return a new customer."""

    customer = Customer(
        customer_ref=customer_ref,
        name=name,
    )

    db.add(customer)

    try:
        db.commit()
        db.refresh(customer)
    except IntegrityError:
        db.rollback()
        raise

    return customer


def create_payment(
    db: Session,
    transaction_ref: str,
    customer_id: int,
    amount: Decimal,
) -> Transaction:
    """Create a payment in PROCESSING status."""

    # Verify that the customer exists.
    customer = db.get(Customer, customer_id)

    if customer is None:
        raise CustomerNotFoundError(
            f"Customer with ID {customer_id} does not exist"
        )

    # Prevent reuse of an existing transaction reference.
    existing_transaction = db.scalar(
        select(Transaction).where(
            Transaction.transaction_ref == transaction_ref
        )
    )

    if existing_transaction is not None:
        raise DuplicateTransactionReferenceError(
            f"Transaction reference {transaction_ref} already exists"
        )

    transaction = Transaction(
        transaction_ref=transaction_ref,
        customer_id=customer_id,
        amount=amount,
        status="PROCESSING",
        created_at=datetime.utcnow(),
        completed_at=None,
        failure_code=None,
    )

    db.add(transaction)

    try:
        db.commit()
        db.refresh(transaction)
    except IntegrityError:
        db.rollback()
        raise

    return transaction
