
"""HTTP routes for MiniPay customer and payment operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from application.api.auth import require_api_key
from application.api.database import get_db

from application.api.models import Customer, Transaction
from application.api.schemas import (
    CustomerCreate,
    CustomerResponse,
    PaymentCreate,
    PaymentResponse,
)
from application.api.services import (
    CustomerNotFoundError,
    DuplicateTransactionReferenceError,
    create_customer,
    create_payment,
)

router = APIRouter(
    prefix="/api",
    tags=["MiniPay API"],
    dependencies=[Depends(require_api_key)],
)


@router.post(
    "/customers",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_customer(
    request: CustomerCreate,
    db: Session = Depends(get_db),
):
    """Register a new customer."""

    try:
        return create_customer(
            db=db,
            customer_ref=request.customer_ref,
            name=request.name,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer reference already exists",
        ) from None


@router.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_payment(
    request: PaymentCreate,
    db: Session = Depends(get_db),
):
    """Submit a new payment."""

    try:
        return create_payment(
            db=db,
            transaction_ref=request.transaction_ref,
            customer_id=request.customer_id,
            amount=request.amount,
        )
    except CustomerNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except DuplicateTransactionReferenceError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/payments/{payment_id}",
    response_model=PaymentResponse,
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve a payment by its database ID."""

    payment = db.get(Transaction, payment_id)

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment


@router.get(
    "/customers/{customer_id}/payments",
    response_model=list[PaymentResponse],
)
def get_customer_payments(
    customer_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve all payments belonging to a customer."""

    customer = db.get(Customer, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    statement = (
        select(Transaction)
        .where(Transaction.customer_id == customer_id)
        .order_by(Transaction.created_at.desc())
    )

    return list(db.scalars(statement).all())
