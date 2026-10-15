"""Servicio de lectura de sūtras."""

from __future__ import annotations

import re
from typing import Any, Optional

import psycopg

from app.schemas.sutra import (
    CrossReferenceOut,
    NoteOut,
    SearchResultItem,
    SutraListItem,
    SutraOut,
)


def _preview(text: str, max_len: int = 120) -> str:
    text = (text or "").strip().replace("\n", " ")
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"


def _looks_like_sutra_id(q: str) -> bool:
    return bool(re.match(r"^\d{1,2}\.\d{1,2}\.\d{1,3}$", q.strip()))


def get_sutra_by_id(conn: psycopg.Connection, sutra_id: str) -> Optional[SutraOut]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, adhyaya, pada, number, sanskrit, translation,
                   order_index, has_tables
            FROM sutras
            WHERE id = %s
            """,
            (sutra_id,),
        )
        row = cur.fetchone()
        if not row:
            return None

        cur.execute(
            """
            SELECT id, note_number, content, note_type, order_index
            FROM notes
            WHERE sutra_id = %s
            ORDER BY order_index, id
            """,
            (sutra_id,),
        )
        notes = [
            NoteOut(
                id=n["id"],
                note_number=n["note_number"],
                content=n["content"],
                note_type=n["note_type"],
                order_index=n["order_index"],
            )
            for n in cur.fetchall()
        ]

        cur.execute(
            """
            SELECT id, to_sutra_ref, reference_text, ref_type, order_index
            FROM cross_references
            WHERE from_sutra_id = %s
            ORDER BY order_index, id
            """,
            (sutra_id,),
        )
        xrefs = [
            CrossReferenceOut(
                id=x["id"],
                to_sutra_ref=x["to_sutra_ref"],
                reference_text=x["reference_text"],
                ref_type=x["ref_type"],
                order_index=x["order_index"],
            )
            for x in cur.fetchall()
        ]

        return SutraOut(
            id=row["id"],
            adhyaya=row["adhyaya"],
            pada=row["pada"],
            number=row["number"],
            sanskrit=row["sanskrit"],
            translation=row["translation"],
            order_index=row["order_index"],
            has_tables=row["has_tables"],
            notes=notes,
            cross_references=xrefs,
        )


def list_sutras(
    conn: psycopg.Connection,
    *,
    adhyaya: Optional[int] = None,
    pada: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[SutraListItem], int]:
    conditions: list[str] = []
    params: list[Any] = []

    if adhyaya is not None:
        conditions.append("s.adhyaya = %s")
        params.append(adhyaya)
    if pada is not None:
        conditions.append("s.pada = %s")
        params.append(pada)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    with conn.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total FROM sutras s {where}", params)
        total = cur.fetchone()["total"]

        cur.execute(
            f"""
            SELECT
                s.id, s.adhyaya, s.pada, s.number, s.sanskrit,
                s.translation, s.order_index,
                COALESCE(n.cnt, 0) AS notes_count
            FROM sutras s
            LEFT JOIN (
                SELECT sutra_id, COUNT(*) AS cnt
                FROM notes
                GROUP BY sutra_id
            ) n ON n.sutra_id = s.id
            {where}
            ORDER BY s.order_index
            LIMIT %s OFFSET %s
            """,
            [*params, limit, offset],
        )
        rows = cur.fetchall()

    items = [
        SutraListItem(
            id=r["id"],
            adhyaya=r["adhyaya"],
            pada=r["pada"],
            number=r["number"],
            sanskrit=r["sanskrit"],
            translation_preview=_preview(r["translation"]),
            order_index=r["order_index"],
            notes_count=r["notes_count"],
        )
        for r in rows
    ]
    return items, total


def search_sutras(
    conn: psycopg.Connection,
    query: str,
    *,
    limit: int = 30,
    offset: int = 0,
) -> tuple[list[SearchResultItem], int]:
    q = query.strip()
    if not q:
        return [], 0

    if _looks_like_sutra_id(q):
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, adhyaya, pada, number, sanskrit, translation
                FROM sutras
                WHERE id = %s
                """,
                (q,),
            )
            row = cur.fetchone()
        if not row:
            return [], 0
        item = SearchResultItem(
            id=row["id"],
            adhyaya=row["adhyaya"],
            pada=row["pada"],
            number=row["number"],
            sanskrit=row["sanskrit"],
            translation_preview=_preview(row["translation"]),
            match_in="sanskrit",
        )
        return [item], 1

    like = f"%{q}%"
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(DISTINCT s.id) AS total
            FROM sutras s
            LEFT JOIN notes n ON n.sutra_id = s.id
            WHERE
                s.sanskrit ILIKE %s
                OR s.translation ILIKE %s
                OR n.content ILIKE %s
            """,
            (like, like, like),
        )
        total = cur.fetchone()["total"]

        cur.execute(
            """
            SELECT DISTINCT ON (s.order_index)
                s.id, s.adhyaya, s.pada, s.number, s.sanskrit, s.translation,
                CASE
                    WHEN s.sanskrit ILIKE %s THEN 'sanskrit'
                    WHEN s.translation ILIKE %s THEN 'translation'
                    ELSE 'note'
                END AS match_in
            FROM sutras s
            LEFT JOIN notes n ON n.sutra_id = s.id
            WHERE
                s.sanskrit ILIKE %s
                OR s.translation ILIKE %s
                OR n.content ILIKE %s
            ORDER BY s.order_index
            LIMIT %s OFFSET %s
            """,
            (like, like, like, like, like, limit, offset),
        )
        rows = cur.fetchall()

    items = [
        SearchResultItem(
            id=r["id"],
            adhyaya=r["adhyaya"],
            pada=r["pada"],
            number=r["number"],
            sanskrit=r["sanskrit"],
            translation_preview=_preview(r["translation"]),
            match_in=r["match_in"],
        )
        for r in rows
    ]
    return items, total


def _looks_like_sutra_id(q: str) -> bool:
    return bool(re.match(r"^\d{1,2}\.\d{1,2}\.\d{1,3}$", q.strip()))


def _preview(text: str, max_len: int = 120) -> str:
    text = (text or "").strip().replace("\n", " ")
    if len(text) <= max_len:
        return text
    return text[: max_len - 1].rstrip() + "…"
