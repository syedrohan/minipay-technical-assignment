
"""Database connection and session management."""

import os
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def get_database_url() -> str:
    """Read the database connection URL from the environment."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not configured")

    return database_url


@lru_cache(maxsize=1)
def get_engine():
    """Create and cache the SQLAlchemy database engine."""
    return create_engine(
        get_database_url(),
        pool_pre_ping=True,
    )


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


def get_db():
    """Provide a database session and close it after use."""
    db = SessionLocal(bind=get_engine())

    try:
        yield db
    finally:
        db.close()
