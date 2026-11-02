
"""SQLAlchemy models matching the MiniPay PostgreSQL schema."""

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)

from application.api.database import Base


class Customer(Base):
    """Represents a MiniPay customer."""

    __tablename__ = "customers"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    customer_ref = Column(String(40), nullable=False, unique=True)
    name = Column(String(120), nullable=False)
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )


class Transaction(Base):
    """Represents a customer payment transaction."""

    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    transaction_ref = Column(String(50), nullable=False)
    customer_id = Column(
        BigInteger,
        ForeignKey("customers.id"),
        nullable=False,
    )
    amount = Column(Numeric(14, 2), nullable=False)
    status = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    failure_code = Column(String(40), nullable=True)

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_transaction_amount"),
        CheckConstraint(
            "status IN ('PROCESSING', 'SUCCESS', 'FAILED')",
            name="check_transaction_status",
        ),
    )


class Callback(Base):
    """Represents a payment callback attempt."""

    __tablename__ = "callbacks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    transaction_id = Column(
        BigInteger,
        ForeignKey("transactions.id"),
        nullable=False,
    )
    attempt_no = Column(Integer, nullable=False)
    http_status = Column(Integer, nullable=True)
    callback_status = Column(String(20), nullable=False)
    attempted_at = Column(DateTime, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "transaction_id",
            "attempt_no",
            name="uq_callback_transaction_attempt",
        ),
        CheckConstraint(
            "callback_status IN ('SUCCESS', 'FAILED')",
            name="check_callback_status",
        ),
    )
