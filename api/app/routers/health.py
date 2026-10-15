"""Health check."""

from __future__ import annotations

from fastapi import APIRouter

from app.db.connection import get_connection
from app.schemas.sutra import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    db_status = "ok"
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
    except Exception:
        db_status = "error"

    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        database=db_status,
    )
