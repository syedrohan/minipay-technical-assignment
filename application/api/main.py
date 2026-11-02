
"""Main entry point for the MiniPay FastAPI application."""

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from application.api.database import get_db
from application.api.routes import router

app = FastAPI(
    title="MiniPay API",
    description="Payment processing and transaction management API",
    version="1.0.0",
)

# Register customer and payment routes.
app.include_router(router)


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Check application and database connectivity."""

    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "unavailable",
            },
        ) from None
