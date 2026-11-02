
"""Verify that the PostgreSQL schema matches our SQLAlchemy models."""

import os

import pytest
from sqlalchemy import create_engine, inspect

from application.api.database import Base
from application.api import models  # noqa: F401


@pytest.fixture
def database_inspector():
    """Connect to the PostgreSQL database created by GitHub Actions."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        pytest.fail("DATABASE_URL environment variable is not configured")

    engine = create_engine(database_url, pool_pre_ping=True)

    try:
        yield inspect(engine)
    finally:
        engine.dispose()


def test_all_model_tables_exist(database_inspector):
    """Check that every SQLAlchemy model table exists in PostgreSQL."""
    actual_tables = set(database_inspector.get_table_names())
    expected_tables = set(Base.metadata.tables.keys())

    assert expected_tables.issubset(actual_tables)


@pytest.mark.parametrize("table_name", ["customers", "transactions", "callbacks"])
def test_model_columns_match_database(database_inspector, table_name):
    """Check that model columns match the actual database columns."""
    actual_columns = {
        column["name"]
        for column in database_inspector.get_columns(table_name)
    }

    expected_columns = set(Base.metadata.tables[table_name].columns.keys())

    assert actual_columns == expected_columns
