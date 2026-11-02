
"""API-key authentication for MiniPay merchant endpoints."""

import os
import secrets

from fastapi import Header, HTTPException, status


def require_api_key(
    x_api_key: str | None = Header(default=None),
) -> None:
    """Validate the API key supplied in the request header."""

    expected_api_key = os.getenv("MINIPAY_API_KEY")

    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is not configured",
        )

    if not x_api_key or not secrets.compare_digest(
        x_api_key,
        expected_api_key,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
