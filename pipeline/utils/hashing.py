"""Utilidades de hashing para integridad de datos."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_text(text: str) -> str:
    """SHA-256 de un string UTF-8. Prefijo 'sha256:' para claridad."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def sha256_file(path: Path | str) -> str:
    """SHA-256 de un archivo (lectura en bloques)."""
    path = Path(path)
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return f"sha256:{h.hexdigest()}"


def normalize_for_hash(text: str) -> str:
    """
    Normalización mínima y reversible antes de hashear un bloque.
    - Colapsa espacios en blanco múltiples a uno solo
    - Elimina espacios al inicio/final de cada línea
    - Conserva saltos de línea
    NO altera diacríticos ni puntuación.
    """
    lines = [line.strip() for line in text.splitlines()]
    while lines and lines[0] == "":
        lines.pop(0)
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)