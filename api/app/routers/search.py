"""Endpoint de búsqueda."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.db.connection import get_connection
from app.schemas.sutra import SearchResponse
from app.services import sutra_service

router = APIRouter(tags=["search"])


@router.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(..., min_length=1, max_length=200, description="Texto o id de sūtra"),
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> SearchResponse:
    with get_connection() as conn:
        items, total = sutra_service.search_sutras(
            conn,
            q,
            limit=limit,
            offset=offset,
        )
    return SearchResponse(query=q, items=items, total=total)
