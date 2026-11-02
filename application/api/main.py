
"""MiniPay FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import text

from application.api.database import get_engine
from application.api.routes import router

app = FastAPI(
    title="MiniPay API",
    description="Payment processing API for MiniPay.",
    version="1.0.0",
)

app.include_router(router)

UI_FILE = Path(__file__).resolve().parents[1] / "ui" / "index.html"


@app.get("/", include_in_schema=False)
def dashboard():
    """Serve the MiniPay browser dashboard."""
    if not UI_FILE.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dashboard file not found",
        )

    return FileResponse(UI_FILE, media_type="text/html")


@app.get("/health")
def health():
    """Check whether the API can connect to the database."""
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))

        return {"status": "healthy", "database": "connected"}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed",
        )
