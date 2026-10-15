#!/usr/bin/env python3
"""
Carga JSONL de anexos → PostgreSQL.

Uso:
  python load_annexes.py \\
    --dir ../data/intermediate \\
    --dsn "postgresql://anselmo@localhost:5433/panini" \\
    [--migrate] [--replace] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    print("ERROR: pip install 'psycopg[binary]'", file=sys.stderr)
    sys.exit(1)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{i}: {exc}") from exc
    return rows


def load_siglas(conn: psycopg.Connection, rows: list[dict], replace: bool) -> int:
    with conn.cursor() as cur:
        if replace:
            # Solo borramos las que vienen en este lote (por id)
            ids = [r["id"] for r in rows if r.get("id")]
            if ids:
                cur.execute("DELETE FROM pratyaharas WHERE id = ANY(%s)", (ids,))
        for r in rows:
            cur.execute(
                """
                INSERT INTO pratyaharas (id, expansion, defined_in, notes, order_index, definition_full)
                VALUES (%(id)s, %(expansion)s, %(defined_in)s, %(notes)s, %(order_index)s, %(definition_full)s)
                ON CONFLICT (id) DO UPDATE SET
                    expansion = EXCLUDED.expansion,
                    defined_in = EXCLUDED.defined_in,
                    notes = EXCLUDED.notes,
                    order_index = EXCLUDED.order_index,
                    definition_full = EXCLUDED.definition_full
                """,
                {
                    "id": r["id"],
                    "expansion": r.get("expansion") or r["id"],
                    "defined_in": r.get("defined_in"),
                    "notes": r.get("notes"),
                    "order_index": r.get("order_index") or 0,
                    "definition_full": r.get("definition_full"),
                },
            )
    return len(rows)


def load_pratyahara_sutras(
    conn: psycopg.Connection, rows: list[dict], replace: bool
) -> int:
    with conn.cursor() as cur:
        if replace:
            cur.execute("TRUNCATE pratyahara_sutras RESTART IDENTITY")
        for r in rows:
            cur.execute(
                """
                INSERT INTO pratyahara_sutras (order_index, sutra_text, definition, generated_siglas)
                VALUES (%(order_index)s, %(sutra_text)s, %(definition)s, %(generated_siglas)s)
                """,
                {
                    "order_index": r.get("order_index") or 0,
                    "sutra_text": r["sutra_text"],
                    "definition": r.get("definition"),
                    "generated_siglas": r.get("generated_siglas"),
                },
            )
    return len(rows)


def load_nominal_bases(
    conn: psycopg.Connection, rows: list[dict], replace: bool
) -> int:
    with conn.cursor() as cur:
        if replace:
            cur.execute("TRUNCATE nominal_bases RESTART IDENTITY")
        for r in rows:
            cur.execute(
                """
                INSERT INTO nominal_bases (
                    base, meaning, notes, order_index,
                    group_name, sutra_ref, item_number
                ) VALUES (
                    %(base)s, %(meaning)s, %(notes)s, %(order_index)s,
                    %(group_name)s, %(sutra_ref)s, %(item_number)s
                )
                """,
                {
                    "base": r["base"],
                    "meaning": r.get("meaning"),
                    "notes": r.get("notes"),
                    "order_index": r.get("order_index") or 0,
                    "group_name": r.get("group_name"),
                    "sutra_ref": r.get("sutra_ref"),
                    "item_number": r.get("item_number"),
                },
            )
    return len(rows)


def load_dhatus(conn: psycopg.Connection, rows: list[dict], replace: bool) -> int:
    with conn.cursor() as cur:
        if replace:
            cur.execute("TRUNCATE dhatus RESTART IDENTITY")
        for r in rows:
            cur.execute(
                """
                INSERT INTO dhatus (
                    root, gana, meaning, markers, raw_entry, order_index,
                    group_label, section_major, subsection, level4, level5,
                    entry_number, detail
                ) VALUES (
                    %(root)s, %(gana)s, %(meaning)s, %(markers)s, %(raw_entry)s, %(order_index)s,
                    %(group_label)s, %(section_major)s, %(subsection)s, %(level4)s, %(level5)s,
                    %(entry_number)s, %(detail)s
                )
                """,
                {
                    "root": r.get("root") or "",
                    "gana": r.get("gana"),
                    "meaning": r.get("meaning"),
                    "markers": r.get("markers"),
                    "raw_entry": r.get("raw_entry"),
                    "order_index": r.get("order_index") or 0,
                    "group_label": r.get("group_label"),
                    "section_major": r.get("section_major"),
                    "subsection": r.get("subsection"),
                    "level4": r.get("level4"),
                    "level5": r.get("level5"),
                    "entry_number": r.get("entry_number"),
                    "detail": r.get("detail"),
                },
            )
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description="Carga anexos JSONL → PostgreSQL")
    parser.add_argument("--dir", required=True, help="Directorio con los JSONL")
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--migrate", action="store_true", help="Aplica 002_annexes.sql")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    d = Path(args.dir)
    files = {
        "siglas.jsonl": ("siglas", load_siglas),
        "pratyahara_sutras.jsonl": ("pratyahara_sutras", load_pratyahara_sutras),
        "nominal_bases.jsonl": ("nominal_bases", load_nominal_bases),
        "dhatus.jsonl": ("dhatus", load_dhatus),
    }

    pending: list[tuple[str, list[dict], Any]] = []
    for name, (label, loader) in files.items():
        path = d / name
        if not path.exists():
            print(f"⚠ No encontrado: {path}")
            continue
        rows = read_jsonl(path)
        print(f"→ {label}: {len(rows)} registros")
        pending.append((label, rows, loader))

    if args.dry_run:
        print("Dry-run: no se escribe en la BD")
        return 0

    with psycopg.connect(args.dsn) as conn:
        if args.migrate:
            mig = (
                Path(__file__).resolve().parents[1]
                / "db"
                / "migrations"
                / "002_annexes.sql"
            )
            if not mig.exists():
                print(f"ERROR: no existe {mig}", file=sys.stderr)
                return 3
            print(f"→ Migración {mig.name}")
            with conn.cursor() as cur:
                cur.execute(mig.read_text(encoding="utf-8"))
            conn.commit()

        for label, rows, loader in pending:
            n = loader(conn, rows, args.replace)
            print(f"  ✓ {label}: {n} cargados")
        conn.commit()

    print("Carga de anexos completada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())