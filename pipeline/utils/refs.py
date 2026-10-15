"""
Extracción de referencias cruzadas a sūtras.

Detecta patrones del tipo:
  1.1.70
  1.1.3-6
  1.1.3-6,73
  6.1.88-92
  7.2.1-7,114-18
  etc.
"""

from __future__ import annotations

import re
from typing import Iterator

from models import CrossReference, RefType  # noqa: E402  (path set by caller)

SUTRA_REF_RE = re.compile(
    r"""
    (?<![.\d])                  # no parte de un número más largo
    (
        \d{1,2}\.\d{1,2}\.      # adhyaya.pada.
        (?:
            \d+                 # número simple
            (?:-\d+)?           # opcional rango
            (?:                 # opcional lista de más números/rangos
                ,\s*
                \d+
                (?:-\d+)?
            )*
        )
    )
    (?![.\d])                   # no seguido de más dígitos/puntos
    """,
    re.VERBOSE,
)

VIA_HINTS = ("mediante", "por", "según", "vía", "via")
OCCURS_HINTS = ("ocurre en", "aparece en", "se encuentra en", "en")
SEE_HINTS = ("véase", "vease", "cf.", "cf ", "ver")
ANUVRTTI_HINTS = ("anuvṛtti", "anuvrtti", "recurre", "recurrencia")


def classify_ref_type(context: str) -> RefType:
    """Clasifica el tipo de referencia según palabras cercanas."""
    ctx = context.lower()
    for h in ANUVRTTI_HINTS:
        if h in ctx:
            return RefType.ANUVRTTI
    for h in VIA_HINTS:
        if h in ctx:
            return RefType.VIA
    for h in OCCURS_HINTS:
        if h in ctx:
            return RefType.OCCURS_IN
    for h in SEE_HINTS:
        if h in ctx:
            return RefType.SEE
    return RefType.OTHER


def extract_references(text: str) -> list[CrossReference]:
    """
    Extrae todas las referencias a sūtras de un texto.
    Devuelve lista de CrossReference con order_index relativo.
    """
    refs: list[CrossReference] = []
    seen: set[str] = set()

    for i, match in enumerate(SUTRA_REF_RE.finditer(text)):
        ref_text = match.group(1).strip()
        if ref_text in seen:
            continue
        seen.add(ref_text)

        start = max(0, match.start() - 40)
        end = min(len(text), match.end() + 20)
        context = text[start:end]

        refs.append(
            CrossReference(
                to=ref_text,
                type=classify_ref_type(context),
                text=context.strip(),
                order_index=i,
            )
        )

    return refs


def iter_individual_sutra_ids(ref: str) -> Iterator[str]:
    """
    Expande una referencia posiblemente compuesta en IDs individuales.
    '1.1.3-6' → 1.1.3, 1.1.4, 1.1.5, 1.1.6
    '1.1.3-6,73' → 1.1.3 … 1.1.6, 1.1.73
    """
    parts = [p.strip() for p in ref.split(",")]
    for part in parts:
        if "-" in part:
            m = re.match(r"^(\d+\.\d+\.)(\d+)-(\d+)$", part)
            if m:
                prefix, start_s, end_s = m.groups()
                start, end = int(start_s), int(end_s)
                if start <= end and end - start < 50:
                    for n in range(start, end + 1):
                        yield f"{prefix}{n}"
                else:
                    yield part
            else:
                yield part
        else:
            yield part