"""Schemas de respuesta para sūtras."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class NoteOut(BaseModel):
    id: int
    note_number: Optional[int] = None
    content: str
    note_type: Optional[str] = None
    order_index: int


class CrossReferenceOut(BaseModel):
    id: int
    to_sutra_ref: str
    reference_text: Optional[str] = None
    ref_type: Optional[str] = None
    order_index: int


class SutraOut(BaseModel):
    id: str
    adhyaya: int
    pada: int
    number: int
    sanskrit: str
    translation: str
    order_index: int
    has_tables: bool
    notes: list[NoteOut] = Field(default_factory=list)
    cross_references: list[CrossReferenceOut] = Field(default_factory=list)


class SutraListItem(BaseModel):
    id: str
    adhyaya: int
    pada: int
    number: int
    sanskrit: str
    translation_preview: str
    order_index: int
    notes_count: int = 0


class SutraListResponse(BaseModel):
    items: list[SutraListItem]
    total: int
    adhyaya: Optional[int] = None
    pada: Optional[int] = None


class SearchResultItem(BaseModel):
    id: str
    adhyaya: int
    pada: int
    number: int
    sanskrit: str
    translation_preview: str
    match_in: str  # 'sanskrit' | 'translation' | 'note'


class SearchResponse(BaseModel):
    query: str
    items: list[SearchResultItem]
    total: int


class HealthResponse(BaseModel):
    status: str
    database: str
