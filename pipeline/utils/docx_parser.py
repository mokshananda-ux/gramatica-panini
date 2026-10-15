"""
Parser de .docx orientado a la estructura de la Gramática de Pāṇini.

Heurísticas principales (según descripción del autor):
- Número de sūtra + texto sánscrito → negrita
- Párrafo principal de traducción → tamaño ≈ 12 pt
- Comentarios / notas / ejemplos → tamaño ≈ 10 pt
- Notas numeradas suelen empezar por "1. ", "2. ", etc.

El parser es conservador: nunca modifica el texto original.
Solo lo estructura y genera raw_block + content_hash.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from docx import Document
from docx.text.paragraph import Paragraph
from docx.text.run import Run

from models import (  # noqa: E402
    ExtractionReport,
    Note,
    NoteType,
    Sutra,
)
from utils.hashing import normalize_for_hash, sha256_file, sha256_text  # noqa: E402
from utils.refs import extract_references  # noqa: E402

# ---------------------------------------------------------------------------
# Constantes y patrones
# ---------------------------------------------------------------------------

SUTRA_ID_RE = re.compile(
    r"^(\d{1,2})\.(\d{1,2})\.(\d{1,3})\s+(.+)$",
    re.DOTALL,
)

NOTE_START_RE = re.compile(r"^(\d+)\.\s+(.*)$", re.DOTALL)

SIZE_MAIN_MIN = 11.0
SIZE_MAIN_MAX = 13.0
SIZE_NOTE_MAX = 10.5


# ---------------------------------------------------------------------------
# Utilidades de estilo
# ---------------------------------------------------------------------------

def _run_font_size_pt(run: Run) -> Optional[float]:
    if run.font.size is not None:
        return run.font.size.pt
    return None


def _paragraph_is_bold(paragraph: Paragraph) -> bool:
    runs = [r for r in paragraph.runs if r.text.strip()]
    if not runs:
        return False
    bold_chars = sum(len(r.text) for r in runs if r.bold)
    total_chars = sum(len(r.text) for r in runs)
    return total_chars > 0 and (bold_chars / total_chars) >= 0.6


def _paragraph_dominant_size(paragraph: Paragraph) -> Optional[float]:
    size_weight: dict[float, int] = {}
    for run in paragraph.runs:
        text = run.text
        if not text.strip():
            continue
        size = _run_font_size_pt(run)
        if size is not None:
            size_weight[size] = size_weight.get(size, 0) + len(text)
    if not size_weight:
        return None
    return max(size_weight, key=size_weight.get)  # type: ignore[arg-type]


def _is_main_translation_size(size: Optional[float]) -> bool:
    if size is None:
        return False
    return SIZE_MAIN_MIN <= size <= SIZE_MAIN_MAX


def _is_note_size(size: Optional[float]) -> bool:
    if size is None:
        return True
    return size <= SIZE_NOTE_MAX


# ---------------------------------------------------------------------------
# Estado del parser
# ---------------------------------------------------------------------------

@dataclass
class ParagraphInfo:
    text: str
    is_bold: bool
    size_pt: Optional[float]
    original_index: int


@dataclass
class ParserState:
    current_sutra_id: Optional[str] = None
    current_adhyaya: Optional[int] = None
    current_pada: Optional[int] = None
    current_number: Optional[int] = None
    current_sanskrit: Optional[str] = None
    translation_parts: list[str] = field(default_factory=list)
    note_parts: list[tuple[Optional[int], str]] = field(default_factory=list)
    raw_lines: list[str] = field(default_factory=list)
    order_index: int = 0
    sutras: list[Sutra] = field(default_factory=list)
    report: Optional[ExtractionReport] = None

    def reset_block(self) -> None:
        self.current_sutra_id = None
        self.current_adhyaya = None
        self.current_pada = None
        self.current_number = None
        self.current_sanskrit = None
        self.translation_parts = []
        self.note_parts = []
        self.raw_lines = []


# ---------------------------------------------------------------------------
# Clasificación de notas
# ---------------------------------------------------------------------------

def _guess_note_type(content: str) -> NoteType:
    lower = content.lower()
    if any(
        k in lower
        for k in (
            "denota", "representa", "significa",
            "término técnico", "t. t.", "t.t.",
        )
    ):
        return NoteType.DEFINITION
    if any(
        k in lower
        for k in ("ejemplo", "por ejemplo", "tenemos", "secuencia", "formación")
    ):
        return NoteType.EXAMPLE
    if any(
        k in lower
        for k in ("ocurre en", "aparece en", "mediante", "véase", "cf.")
    ):
        return NoteType.REFERENCE
    if any(
        k in lower
        for k in ("significado usual", "etimolog", "cf.", "literalmente")
    ):
        return NoteType.PHILOLOGICAL
    if any(
        k in lower
        for k in ("meta-regla", "metarregla", "anuvṛtti", "recurre", "opera en")
    ):
        return NoteType.META_RULE
    return NoteType.OTHER


# ---------------------------------------------------------------------------
# Construcción de un Sutra a partir del estado
# ---------------------------------------------------------------------------

def _flush_sutra(state: ParserState) -> None:
    if not state.current_sutra_id or not state.current_sanskrit:
        return

    translation = "\n\n".join(p.strip() for p in state.translation_parts if p.strip())
    if not translation:
        translation = "(sin traducción principal detectada)"
        if state.report:
            state.report.add_warning(
                "warning",
                "Sūtra sin párrafo de traducción principal detectado",
                state.current_sutra_id,
            )

    notes: list[Note] = []
    for idx, (num, content) in enumerate(state.note_parts):
        content = content.strip()
        if not content:
            continue
        notes.append(
            Note(
                number=num,
                content=content,
                type=_guess_note_type(content),
                order_index=idx,
            )
        )

    raw_block = "\n".join(state.raw_lines)
    normalized = normalize_for_hash(raw_block)
    content_hash = sha256_text(normalized)

    all_text = translation + "\n" + "\n".join(n.content for n in notes)
    cross_refs = extract_references(all_text)

    try:
        sutra = Sutra(
            id=state.current_sutra_id,
            adhyaya=state.current_adhyaya,  # type: ignore[arg-type]
            pada=state.current_pada,  # type: ignore[arg-type]
            number=state.current_number,  # type: ignore[arg-type]
            sanskrit=state.current_sanskrit,
            translation=translation,
            notes=notes,
            cross_references=cross_refs,
            raw_block=raw_block,
            content_hash=content_hash,
            order_index=state.order_index,
            has_tables=False,
        )
        state.sutras.append(sutra)
        state.order_index += 1
    except Exception as exc:
        if state.report:
            state.report.add_warning(
                "error",
                f"No se pudo construir el sūtra: {exc}",
                state.current_sutra_id,
            )


# ---------------------------------------------------------------------------
# Parser principal
# ---------------------------------------------------------------------------

def parse_docx(path: Path | str) -> tuple[list[Sutra], ExtractionReport]:
    """
    Parsea un .docx y devuelve la lista de Sutra + informe de extracción.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")

    source_hash = sha256_file(path)
    report = ExtractionReport(
        source_file=str(path),
        source_hash=source_hash,
        started_at=__import__("datetime").datetime.utcnow(),
    )

    doc = Document(str(path))
    state = ParserState(report=report)

    paragraphs: list[ParagraphInfo] = []
    for i, para in enumerate(doc.paragraphs):
        text = para.text.replace("\xa0", " ").strip()
        if not text:
            continue
        paragraphs.append(
            ParagraphInfo(
                text=text,
                is_bold=_paragraph_is_bold(para),
                size_pt=_paragraph_dominant_size(para),
                original_index=i,
            )
        )

    for pinfo in paragraphs:
        text = pinfo.text

        if pinfo.is_bold:
            m = SUTRA_ID_RE.match(text)
            if m:
                _flush_sutra(state)
                state.reset_block()

                adhyaya = int(m.group(1))
                pada = int(m.group(2))
                number = int(m.group(3))
                sanskrit = m.group(4).strip()

                state.current_sutra_id = f"{adhyaya}.{pada}.{number}"
                state.current_adhyaya = adhyaya
                state.current_pada = pada
                state.current_number = number
                state.current_sanskrit = sanskrit
                state.raw_lines.append(text)
                continue

        if not state.current_sutra_id:
            continue

        state.raw_lines.append(text)

        if _is_main_translation_size(pinfo.size_pt) and not state.note_parts:
            state.translation_parts.append(text)
        elif _is_note_size(pinfo.size_pt) or state.note_parts:
            m_note = NOTE_START_RE.match(text)
            if m_note:
                num = int(m_note.group(1))
                content = m_note.group(2)
                state.note_parts.append((num, content))
            else:
                if state.note_parts:
                    prev_num, prev_content = state.note_parts[-1]
                    state.note_parts[-1] = (
                        prev_num,
                        prev_content + "\n" + text,
                    )
                else:
                    state.note_parts.append((None, text))
        else:
            if not state.note_parts:
                state.translation_parts.append(text)
            else:
                if state.note_parts:
                    prev_num, prev_content = state.note_parts[-1]
                    state.note_parts[-1] = (
                        prev_num,
                        prev_content + "\n" + text,
                    )
                else:
                    state.note_parts.append((None, text))

    _flush_sutra(state)

    report.sutras_found = len(state.sutras)
    report.notes_found = sum(len(s.notes) for s in state.sutras)
    report.cross_refs_found = sum(len(s.cross_references) for s in state.sutras)
    report.finished_at = __import__("datetime").datetime.utcnow()
    report.status = "success" if state.sutras else "failed"

    if not state.sutras:
        report.add_warning(
            "error",
            "No se detectó ningún sūtra. Revisa que el número + texto estén en negrita.",
        )

    return state.sutras, report


# ---------------------------------------------------------------------------
# Helper para pruebas con texto plano (sin .docx)
# ---------------------------------------------------------------------------

def parse_plain_blocks(blocks: list[dict]) -> list[Sutra]:
    """
    Útil para tests unitarios o cuando se tiene el texto ya segmentado.

    Cada bloque es un dict con:
      - id, sanskrit, translation, notes (lista de str o de dict)
    """
    from utils.hashing import normalize_for_hash, sha256_text

    sutras: list[Sutra] = []
    for order, block in enumerate(blocks):
        sid = block["id"]
        parts = sid.split(".")
        adhyaya, pada, number = int(parts[0]), int(parts[1]), int(parts[2])

        notes_raw = block.get("notes", [])
        notes: list[Note] = []
        for i, n in enumerate(notes_raw):
            if isinstance(n, str):
                m = NOTE_START_RE.match(n)
                if m:
                    notes.append(
                        Note(
                            number=int(m.group(1)),
                            content=m.group(2).strip(),
                            type=_guess_note_type(m.group(2)),
                            order_index=i,
                        )
                    )
                else:
                    notes.append(
                        Note(
                            number=None,
                            content=n.strip(),
                            type=_guess_note_type(n),
                            order_index=i,
                        )
                    )
            else:
                notes.append(Note(**n))

        translation = block["translation"]
        raw = block.get("raw_block") or (
            f"{sid} {block['sanskrit']}\n{translation}\n"
            + "\n".join(
                (f"{n.number}. {n.content}" if n.number else n.content)
                for n in notes
            )
        )
        content_hash = sha256_text(normalize_for_hash(raw))
        cross_refs = extract_references(
            translation + "\n" + "\n".join(n.content for n in notes)
        )

        sutras.append(
            Sutra(
                id=sid,
                adhyaya=adhyaya,
                pada=pada,
                number=number,
                sanskrit=block["sanskrit"],
                translation=translation,
                notes=notes,
                cross_references=cross_refs,
                raw_block=raw,
                content_hash=content_hash,
                order_index=order,
            )
        )
    return sutras