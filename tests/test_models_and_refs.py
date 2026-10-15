#!/usr/bin/env python3
"""Tests unitarios de modelos y extracción de referencias (sin .docx)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))

from models import NoteType, Sutra
from utils.docx_parser import parse_plain_blocks
from utils.refs import extract_references, iter_individual_sutra_ids


def test_extract_references_basic():
    text = (
        "Como un t. t. vṛ́d-dhi ocurre en 1.1.3-6,73; 6.1.88-92; "
        "2.105; 7.2.1-7,114-18; 3.1-35, 89-90."
    )
    refs = extract_references(text)
    assert len(refs) >= 3
    tos = {r.to for r in refs}
    assert "1.1.3-6,73" in tos or any("1.1.3" in t for t in tos)
    print("✓ extract_references_basic")


def test_expand_range():
    ids = list(iter_individual_sutra_ids("1.1.3-6"))
    assert ids == ["1.1.3", "1.1.4", "1.1.5", "1.1.6"]
    print("✓ expand_range")


def test_parse_plain_blocks_sample():
    blocks = [
        {
            "id": "1.1.1",
            "sanskrit": "vṛ́d-dhir āT—aiC",
            "translation": (
                "(El término técnico = t. t.) vṛ́d-dhi denota los fonemas "
                "vocálicos ‘ā’ larga (= āT) y los diptongos ‘ai’ y ‘au’ (= aiC)."
            ),
            "notes": [
                "1. āT = a la clase de fonemas representada por la vocal larga ‘ā’ "
                "(mediante 1.1.70 abajo) con características supra-segmentales…",
                "2. aiC = representa los diptongos ‘ai’ y ‘au’, mediante 1.1.70.",
                "3. El significado usual del término vṛ́d-dhi es “incremento, crecimiento…",
                "4. Como un t. t. vṛ́d-dhi ocurre en 1.1.3-6,73; 6.1.88-92; 2.105; "
                "7.2.1-7,114-18; 3.1-35, 89-90.",
            ],
        },
        {
            "id": "1.1.2",
            "sanskrit": "aT—eṄ guṇáḥ",
            "translation": (
                "(El t. t.) guṇá denota los fonemas vocálicos ‘a’ corta (aT) "
                "y los diptongos ‘e’ y ‘o’ (eṄ)."
            ),
            "notes": [
                "1. aT = a la clase de fonemas representados por ‘a’ corta…",
                "2. El significado usual del término guṇá es “cualidad, atributo…",
                "3. Como un t. t. guṇá ocurre en 1.1.3-6; 6.1.87, 97; …",
            ],
        },
        {
            "id": "1.1.3",
            "sanskrit": "iKo guṇá-vṛd-dhī́",
            "translation": (
                "Cuando los t. t. guṇá (2) y vṛ́d-dhi (1) se emplean como morfemas "
                "reemplazos… estos reemplazan solamente a las vocales denotadas "
                "por la sigla iK (= i, u, ṛ, ḷ)."
            ),
            "notes": [],
        },
    ]

    sutras = parse_plain_blocks(blocks)
    assert len(sutras) == 3
    assert sutras[0].id == "1.1.1"
    assert sutras[0].adhyaya == 1
    assert sutras[0].pada == 1
    assert sutras[0].number == 1
    assert "vṛ́d-dhi" in sutras[0].translation
    assert len(sutras[0].notes) == 4
    assert sutras[0].notes[0].number == 1
    assert sutras[0].notes[0].type in (NoteType.DEFINITION, NoteType.OTHER)
    assert sutras[0].content_hash.startswith("sha256:")
    assert len(sutras[0].cross_references) >= 1

    for s in sutras:
        data = s.model_dump()
        restored = Sutra.model_validate(data)
        assert restored.id == s.id

    print("✓ parse_plain_blocks_sample")
    print(f"  Sūtra 1.1.1 → {len(sutras[0].notes)} notas, "
          f"{len(sutras[0].cross_references)} referencias")
    print(f"  Hash: {sutras[0].content_hash[:40]}…")


if __name__ == "__main__":
    test_extract_references_basic()
    test_expand_range()
    test_parse_plain_blocks_sample()
    print("\nTodos los tests pasaron.")