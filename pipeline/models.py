"""
Modelos Pydantic para el formato intermedio de la Gramática de Pāṇini.

Estos modelos son la fuente de verdad estructurada entre el .docx
y PostgreSQL. Toda extracción debe validarse contra ellos.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class NoteType(str, Enum):
    DEFINITION = "definition"
    EXAMPLE = "example"
    REFERENCE = "reference"
    PHILOLOGICAL = "philological"
    META_RULE = "meta_rule"
    OTHER = "other"


class RefType(str, Enum):
    OCCURS_IN = "occurs_in"
    VIA = "via"
    SEE = "see"
    ANUVRTTI = "anuvrtti"
    EXAMPLE = "example"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Notas / comentarios (normalmente cuerpo 10 pt)
# ---------------------------------------------------------------------------

class Note(BaseModel):
    number: Optional[int] = Field(
        default=None,
        description="Número de la nota (1, 2, 3…). None si no está numerada.",
    )
    content: str = Field(..., min_length=1)
    type: NoteType = NoteType.OTHER
    order_index: int = Field(..., ge=0)

    @field_validator("content")
    @classmethod
    def strip_content(cls, v: str) -> str:
        return v.strip()


# ---------------------------------------------------------------------------
# Referencias cruzadas
# ---------------------------------------------------------------------------

class CrossReference(BaseModel):
    to: str = Field(
        ...,
        description="Referencia textual: '1.1.70', '1.1.3-6', '7.3.84', etc.",
    )
    type: RefType = RefType.OTHER
    text: Optional[str] = Field(
        default=None,
        description="Fragmento original donde aparece la referencia.",
    )
    order_index: int = Field(default=0, ge=0)

    @field_validator("to")
    @classmethod
    def normalize_ref(cls, v: str) -> str:
        return v.strip()


# ---------------------------------------------------------------------------
# Sūtra
# ---------------------------------------------------------------------------

class Sutra(BaseModel):
    id: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    adhyaya: int = Field(..., ge=1, le=8)
    pada: int = Field(..., ge=1, le=4)
    number: int = Field(..., ge=1)
    sanskrit: str = Field(..., min_length=1)
    translation: str = Field(..., min_length=1)
    notes: list[Note] = Field(default_factory=list)
    cross_references: list[CrossReference] = Field(default_factory=list)
    raw_block: str = Field(..., min_length=1)
    content_hash: str = Field(..., min_length=10)
    order_index: int = Field(..., ge=0)
    has_tables: bool = False

    @model_validator(mode="after")
    def check_id_consistency(self) -> "Sutra":
        expected = f"{self.adhyaya}.{self.pada}.{self.number}"
        if self.id != expected:
            raise ValueError(
                f"id '{self.id}' no coincide con "
                f"adhyaya.pada.number = '{expected}'"
            )
        return self

    @field_validator("sanskrit", "translation", "raw_block")
    @classmethod
    def strip_text(cls, v: str) -> str:
        return v.strip()


# ---------------------------------------------------------------------------
# Anexos
# ---------------------------------------------------------------------------

class Pratyahara(BaseModel):
    id: str = Field(..., min_length=1)  # 'āT', 'aiC', 'iK'…
    expansion: str = Field(..., min_length=1)
    defined_in: Optional[str] = Field(
        default=None,
        pattern=r"^\d+\.\d+\.\d+$",
    )
    notes: Optional[str] = None


class Dhatu(BaseModel):
    root: str = Field(..., min_length=1)
    gana: Optional[int] = Field(default=None, ge=1, le=10)
    meaning: Optional[str] = None
    markers: Optional[str] = None
    raw_entry: Optional[str] = None
    order_index: int = Field(..., ge=0)


class NominalBase(BaseModel):
    base: str = Field(..., min_length=1)
    meaning: Optional[str] = None
    notes: Optional[str] = None
    order_index: int = Field(..., ge=0)


class EmbeddedTable(BaseModel):
    sutra_id: Optional[str] = Field(default=None, pattern=r"^\d+\.\d+\.\d+$")
    annex_type: Optional[str] = None
    caption: Optional[str] = None
    table_data: dict | list  # JSON flexible
    order_index: int = Field(..., ge=0)


# ---------------------------------------------------------------------------
# Informe de extracción (auditoría)
# ---------------------------------------------------------------------------

class ExtractionWarning(BaseModel):
    level: str  # 'info' | 'warning' | 'error'
    message: str
    context: Optional[str] = None  # id de sūtra o posición


class ExtractionReport(BaseModel):
    source_file: str
    source_hash: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    sutras_found: int = 0
    notes_found: int = 0
    cross_refs_found: int = 0
    tables_found: int = 0
    warnings: list[ExtractionWarning] = Field(default_factory=list)
    status: str = "running"  # running | success | partial | failed

    def add_warning(
        self,
        level: str,
        message: str,
        context: Optional[str] = None,
    ) -> None:
        self.warnings.append(
            ExtractionWarning(level=level, message=message, context=context)
        )