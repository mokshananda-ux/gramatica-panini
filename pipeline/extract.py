#!/usr/bin/env python3
"""
Punto de entrada del pipeline de extracción.

Uso:
    python extract.py --source /ruta/a/gramatica.docx --out data/intermediate

Genera:
    - sutras.jsonl
    - extraction_report.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models import Sutra
from utils.docx_parser import parse_docx
from utils.hashing import sha256_file


def write_jsonl(path: Path, items: list[Sutra]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for item in items:
            f.write(item.model_dump_json() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extrae sūtras de un .docx de la Gramática de Pāṇini"
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Ruta al archivo .docx",
    )
    parser.add_argument(
        "--out",
        default="data/intermediate",
        help="Directorio de salida (default: data/intermediate)",
    )
    parser.add_argument(
        "--pretty-report",
        action="store_true",
        help="Imprime el informe de extracción en consola",
    )
    args = parser.parse_args()

    source = Path(args.source)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not source.exists():
        print(f"ERROR: no existe {source}", file=sys.stderr)
        return 1

    print(f"→ Extrayendo de: {source}")
    print(f"  Hash del archivo: {sha256_file(source)}")

    try:
        sutras, report = parse_docx(source)
    except Exception as exc:
        print(f"ERROR durante el parseo: {exc}", file=sys.stderr)
        return 2

    sutras_path = out_dir / "sutras.jsonl"
    write_jsonl(sutras_path, sutras)
    print(f"→ {len(sutras)} sūtras escritos en {sutras_path}")

    report_path = out_dir / "extraction_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2))
    print(f"→ Informe: {report_path}")

    if args.pretty_report:
        print("\n========== INFORME ==========")
        print(f"Estado        : {report.status}")
        print(f"Sūtras        : {report.sutras_found}")
        print(f"Notas         : {report.notes_found}")
        print(f"Referencias   : {report.cross_refs_found}")
        print(f"Tablas        : {report.tables_found}")
        if report.warnings:
            print("\nAvisos:")
            for w in report.warnings:
                ctx = f" [{w.context}]" if w.context else ""
                print(f"  [{w.level.upper()}]{ctx} {w.message}")
        print("=============================\n")

    return 0 if report.status in ("success", "partial") else 3


if __name__ == "__main__":
    raise SystemExit(main())