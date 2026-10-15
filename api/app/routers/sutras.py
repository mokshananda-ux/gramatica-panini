"""Endpoints de sūtras."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.db.connection import get_connection
from app.schemas.sutra import SutraListResponse, SutraOut
from app.services import sutra_service

router = APIRouter(prefix="/sutras", tags=["sutras"])


@router.get("", response_model=SutraListResponse)
def list_sutras(
    adhyaya: Optional[int] = Query(None, ge=1, le=8),
    pada: Optional[int] = Query(None, ge=1, le=4),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> SutraListResponse:
    with get_connection() as conn:
        items, total = sutra_service.list_sutras(
            conn,
            adhyaya=adhyaya,
            pada=pada,
            limit=limit,
            offset=offset,
        )
    return SutraListResponse(
        items=items,
        total=total,
        adhyaya=adhyaya,
        pada=pada,
    )


@router.get("/{sutra_id}", response_model=SutraOut)
def get_sutra(sutra_id: str) -> SutraOut:
    with get_connection() as conn:
        sutra = sutra_service.get_sutra_by_id(conn, sutra_id)
    if not sutra:
        raise HTTPException(status_code=404, detail=f"Sūtra {sutra_id} no encontrado")
    return sutra
