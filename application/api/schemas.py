
"""Pydantic request and response schemas for MiniPay."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------- Customer schemas ----------

class CustomerCreate(BaseModel):
    """Validate a new customer request."""

    customer_ref: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=120)


class CustomerResponse(BaseModel):
    """Return customer information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer_ref: str
    name: str
    created_at: datetime


# ---------- Payment schemas ----------

class PaymentCreate(BaseModel):
    """Validate a new payment request."""

    transaction_ref: str = Field(min_length=1, max_length=50)
    customer_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


class PaymentResponse(BaseModel):
    """Return payment transaction information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_ref: str
    customer_id: int
    amount: Decimal
    status: Literal["PROCESSING", "SUCCESS", "FAILED"]
    created_at: datetime
    completed_at: datetime | None
    failure_code: str | None


# ---------- Callback schemas ----------

class CallbackResponse(BaseModel):
    """Return payment callback attempt information."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    transaction_id: int
    attempt_no: int
    http_status: int | None
    callback_status: Literal["SUCCESS", "FAILED"]
    attempted_at: datetime
