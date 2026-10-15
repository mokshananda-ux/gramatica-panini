"""Endpoints de anexos: pratyāhāras, dhātu-pāṭha, bases nominales."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query

from app.db.connection import get_connection

router = APIRouter(prefix="/annexes", tags=["annexes"])


@router.get("/pratyaharas")
def list_pratyaharas() -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, expansion, defined_in, notes,
                       order_index, definition_full
                FROM pratyaharas
                ORDER BY COALESCE(order_index, 999), id
                """
            )
            return list(cur.fetchall())


@router.get("/pratyaharas/{pratyahara_id}")
def get_pratyahara(pratyahara_id: str) -> dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, expansion, defined_in, notes,
                       order_index, definition_full
                FROM pratyaharas
                WHERE id = %s
                """,
                (pratyahara_id,),
            )
            row = cur.fetchone()
    if not row:
        raise HTTPException(
            status_code=404, detail=f"Pratyāhāra {pratyahara_id} no encontrado"
        )
    return row


@router.get("/pratyahara-sutras")
def list_pratyahara_sutras() -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, order_index, sutra_text, definition, generated_siglas
                FROM pratyahara_sutras
                ORDER BY order_index, id
                """
            )
            return list(cur.fetchall())


@router.get("/dhatus")
def list_dhatus(
    gana: Optional[int] = Query(None, ge=1, le=10),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    conditions: list[str] = []
    params: list[Any] = []
    if gana is not None:
        conditions.append("gana = %s")
        params.append(gana)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS total FROM dhatus {where}", params)
            total = cur.fetchone()["total"]
            cur.execute(
                f"""
                SELECT id, root, gana, meaning, markers, order_index,
                       group_label, section_major, subsection,
                       level4, level5, entry_number, detail
                FROM dhatus
                {where}
                ORDER BY order_index, id
                LIMIT %s OFFSET %s
                """,
                [*params, limit, offset],
            )
            items = list(cur.fetchall())
    return {"items": items, "total": total, "gana": gana}


@router.get("/nominal-bases")
def list_nominal_bases(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM nominal_bases")
            total = cur.fetchone()["total"]
            cur.execute(
                """
                SELECT id, base, meaning, notes, order_index,
                       group_name, sutra_ref, item_number
                FROM nominal_bases
                ORDER BY order_index, id
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )
            items = list(cur.fetchall())
    return {"items": items, "total": total}
