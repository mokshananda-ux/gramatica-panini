#!/usr/bin/env python3
"""
Carga idempotente de sutras.jsonl → PostgreSQL.

Uso:
    python load.py --jsonl ../data/intermediate/sutras.jsonl \\
                   --dsn "postgresql://user:pass@localhost:5433/panini" \\
                   [--dry-run] [--replace]

Comportamiento:
  - UPSERT por id de sūtra (ON CONFLICT DO UPDATE solo si content_hash cambió).
  - Borra y reinserta notes + cross_references del sūtra afectado.
  - Registra la corrida en pipeline_runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    print(
        "ERROR: falta psycopg. Instala con:\n  pip install 'psycopg[binary]'",
        file=sys.stderr,
    )
    sys.exit(1)

from models import Sutra


# ---------------------------------------------------------------------------
# Lectura del JSONL
# ---------------------------------------------------------------------------

def read_jsonl(path: Path) -> list[Sutra]:
    sutras: list[Sutra] = []
    with path.open(encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                sutras.append(Sutra.model_validate(data))
            except Exception as exc:
                raise ValueError(f"Línea {line_no}: {exc}") from exc
    return sutras


# ---------------------------------------------------------------------------
# Carga
# ---------------------------------------------------------------------------

UPSERT_SUTRA = """
INSERT INTO sutras (
    id, adhyaya, pada, number, sanskrit, translation,
    raw_block, content_hash, order_index, has_tables
) VALUES (
    %(id)s, %(adhyaya)s, %(pada)s, %(number)s, %(sanskrit)s, %(translation)s,
    %(raw_block)s, %(content_hash)s, %(order_index)s, %(has_tables)s
)
ON CONFLICT (id) DO UPDATE SET
    adhyaya      = EXCLUDED.adhyaya,
    pada         = EXCLUDED.pada,
    number       = EXCLUDED.number,
    sanskrit     = EXCLUDED.sanskrit,
    translation  = EXCLUDED.translation,
    raw_block    = EXCLUDED.raw_block,
    content_hash = EXCLUDED.content_hash,
    order_index  = EXCLUDED.order_index,
    has_tables   = EXCLUDED.has_tables,
    updated_at   = now()
WHERE sutras.content_hash IS DISTINCT FROM EXCLUDED.content_hash
RETURNING id, (xmax = 0) AS inserted;
"""

DELETE_NOTES = "DELETE FROM notes WHERE sutra_id = %s"
DELETE_XREFS = "DELETE FROM cross_references WHERE from_sutra_id = %s"

INSERT_NOTE = """
INSERT INTO notes (sutra_id, note_number, content, note_type, order_index)
VALUES (%(sutra_id)s, %(note_number)s, %(content)s, %(note_type)s, %(order_index)s)
"""

INSERT_XREF = """
INSERT INTO cross_references (
    from_sutra_id, to_sutra_ref, reference_text, ref_type, order_index
) VALUES (
    %(from_sutra_id)s, %(to_sutra_ref)s, %(reference_text)s,
    %(ref_type)s, %(order_index)s
)
"""

INSERT_RUN = """
INSERT INTO pipeline_runs (
    source_file, source_hash, started_at, finished_at,
    sutras_loaded, notes_loaded, cross_refs_loaded, status, report
) VALUES (
    %(source_file)s, %(source_hash)s, %(started_at)s, %(finished_at)s,
    %(sutras_loaded)s, %(notes_loaded)s, %(cross_refs_loaded)s,
    %(status)s, %(report)s::jsonb
)
RETURNING id
"""


def load_sutras(
    conn: psycopg.Connection,
    sutras: list[Sutra],
    *,
    source_file: str,
    source_hash: str,
    replace: bool = False,
) -> dict[str, Any]:
    """
    Carga sūtras. Devuelve un resumen.
    Si replace=True, elimina primero todos los sūtras cuyo id esté en el lote.
    """
    started = datetime.now(timezone.utc)
    inserted = 0
    updated = 0
    unchanged = 0
    notes_total = 0
    xrefs_total = 0

    with conn.cursor(row_factory=dict_row) as cur:
        if replace:
            ids = [s.id for s in sutras]
            cur.execute(
                "DELETE FROM sutras WHERE id = ANY(%s)",
                (ids,),
            )

        for s in sutras:
            params = {
                "id": s.id,
                "adhyaya": s.adhyaya,
                "pada": s.pada,
                "number": s.number,
                "sanskrit": s.sanskrit,
                "translation": s.translation,
                "raw_block": s.raw_block,
                "content_hash": s.content_hash,
                "order_index": s.order_index,
                "has_tables": s.has_tables,
            }
            cur.execute(UPSERT_SUTRA, params)
            row = cur.fetchone()

            if row is None:
                # content_hash idéntico → no se tocó el sūtra
                unchanged += 1
            else:
                if row["inserted"]:
                    inserted += 1
                else:
                    updated += 1

            # Siempre regeneramos notas y referencias del sūtra
            cur.execute(DELETE_NOTES, (s.id,))
            cur.execute(DELETE_XREFS, (s.id,))

            for n in s.notes:
                cur.execute(
                    INSERT_NOTE,
                    {
                        "sutra_id": s.id,
                        "note_number": n.number,
                        "content": n.content,
                        "note_type": n.type.value if hasattr(n.type, "value") else n.type,
                        "order_index": n.order_index,
                    },
                )
                notes_total += 1

            for x in s.cross_references:
                cur.execute(
                    INSERT_XREF,
                    {
                        "from_sutra_id": s.id,
                        "to_sutra_ref": x.to,
                        "reference_text": x.text,
                        "ref_type": x.type.value if hasattr(x.type, "value") else x.type,
                        "order_index": x.order_index,
                    },
                )
                xrefs_total += 1

        finished = datetime.now(timezone.utc)
        report = {
            "inserted": inserted,
            "updated": updated,
            "unchanged": unchanged,
            "notes": notes_total,
            "cross_refs": xrefs_total,
        }
        cur.execute(
            INSERT_RUN,
            {
                "source_file": source_file,
                "source_hash": source_hash,
                "started_at": started,
                "finished_at": finished,
                "sutras_loaded": len(sutras),
                "notes_loaded": notes_total,
                "cross_refs_loaded": xrefs_total,
                "status": "success",
                "report": json.dumps(report),
            },
        )
        run_id = cur.fetchone()["id"]

    conn.commit()
    return {
        "run_id": run_id,
        "sutras": len(sutras),
        "inserted": inserted,
        "updated": updated,
        "unchanged": unchanged,
        "notes": notes_total,
        "cross_refs": xrefs_total,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Carga sutras.jsonl en PostgreSQL (idempotente)"
    )
    parser.add_argument(
        "--jsonl",
        required=True,
        help="Ruta al archivo sutras.jsonl",
    )
    parser.add_argument(
        "--dsn",
        required=True,
        help='DSN PostgreSQL, ej. "postgresql://user:pass@localhost:5432/panini"',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo valida el JSONL, no escribe en la BD",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Elimina los sūtras del lote antes de insertar (carga limpia del lote)",
    )
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Ejecuta db/migrations/001_initial.sql antes de cargar",
    )
    args = parser.parse_args()

    jsonl_path = Path(args.jsonl)
    if not jsonl_path.exists():
        print(f"ERROR: no existe {jsonl_path}", file=sys.stderr)
        return 1

    print(f"→ Leyendo {jsonl_path}")
    try:
        sutras = read_jsonl(jsonl_path)
    except Exception as exc:
        print(f"ERROR al leer JSONL: {exc}", file=sys.stderr)
        return 2

    print(f"  {len(sutras)} sūtras validados")

    if args.dry_run:
        print("→ Dry-run: no se escribe en la BD")
        notes = sum(len(s.notes) for s in sutras)
        xrefs = sum(len(s.cross_references) for s in sutras)
        print(f"  Notas: {notes}  |  Referencias: {xrefs}")
        return 0

    print(f"→ Conectando a PostgreSQL…")
    try:
        with psycopg.connect(args.dsn) as conn:
            if args.migrate:
                mig = (
                    Path(__file__).resolve().parents[1]
                    / "db"
                    / "migrations"
                    / "001_initial.sql"
                )
                if not mig.exists():
                    print(f"ERROR: no existe {mig}", file=sys.stderr)
                    return 3
                print(f"→ Ejecutando migración {mig.name}")
                with conn.cursor() as cur:
                    cur.execute(mig.read_text(encoding="utf-8"))
                conn.commit()

            source_hash = "unknown"
            report_path = jsonl_path.parent / "extraction_report.json"
            if report_path.exists():
                try:
                    rep = json.loads(report_path.read_text(encoding="utf-8"))
                    source_hash = rep.get("source_hash", "unknown")
                except Exception:
                    pass

            summary = load_sutras(
                conn,
                sutras,
                source_file=str(jsonl_path),
                source_hash=source_hash,
                replace=args.replace,
            )
    except psycopg.Error as exc:
        print(f"ERROR de base de datos: {exc}", file=sys.stderr)
        return 4

    print("\n========== CARGA COMPLETADA ==========")
    print(f"  Run ID       : {summary['run_id']}")
    print(f"  Sūtras       : {summary['sutras']}")
    print(f"    insertados : {summary['inserted']}")
    print(f"    actualizados: {summary['updated']}")
    print(f"    sin cambio : {summary['unchanged']}")
    print(f"  Notas        : {summary['notes']}")
    print(f"  Referencias  : {summary['cross_refs']}")
    print("======================================\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())