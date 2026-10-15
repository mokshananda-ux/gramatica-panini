-- =============================================================================
-- Gramática de Pāṇini – esquema inicial (PostgreSQL 14+)
-- Migración 001
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- ---------------------------------------------------------------------------
-- SŪTRAS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sutras (
    id              TEXT PRIMARY KEY,
    adhyaya         SMALLINT NOT NULL CHECK (adhyaya BETWEEN 1 AND 8),
    pada            SMALLINT NOT NULL CHECK (pada BETWEEN 1 AND 4),
    number          SMALLINT NOT NULL CHECK (number >= 1),
    sanskrit        TEXT NOT NULL,
    translation     TEXT NOT NULL,
    raw_block       TEXT NOT NULL,
    content_hash    TEXT NOT NULL,
    order_index     INTEGER NOT NULL,
    has_tables      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (adhyaya, pada, number)
);

CREATE INDEX IF NOT EXISTS idx_sutras_adhyaya_pada ON sutras (adhyaya, pada);
CREATE INDEX IF NOT EXISTS idx_sutras_order ON sutras (order_index);
CREATE INDEX IF NOT EXISTS idx_sutras_sanskrit_trgm ON sutras USING GIN (sanskrit gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_sutras_translation_trgm ON sutras USING GIN (translation gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_sutras_fts ON sutras USING GIN (
    to_tsvector('spanish', coalesce(translation, '') || ' ' || coalesce(sanskrit, ''))
);

-- ---------------------------------------------------------------------------
-- NOTAS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notes (
    id              BIGSERIAL PRIMARY KEY,
    sutra_id        TEXT NOT NULL REFERENCES sutras(id) ON DELETE CASCADE,
    note_number     SMALLINT,
    content         TEXT NOT NULL,
    note_type       TEXT,
    order_index     INTEGER NOT NULL DEFAULT 0,
    content_hash    TEXT
);

CREATE INDEX IF NOT EXISTS idx_notes_sutra ON notes (sutra_id);
CREATE INDEX IF NOT EXISTS idx_notes_type  ON notes (note_type);

-- ---------------------------------------------------------------------------
-- REFERENCIAS CRUZADAS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cross_references (
    id              BIGSERIAL PRIMARY KEY,
    from_sutra_id   TEXT NOT NULL REFERENCES sutras(id) ON DELETE CASCADE,
    to_sutra_ref    TEXT NOT NULL,
    reference_text  TEXT,
    ref_type        TEXT,
    order_index     INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_xref_from ON cross_references (from_sutra_id);
CREATE INDEX IF NOT EXISTS idx_xref_to   ON cross_references (to_sutra_ref);

-- ---------------------------------------------------------------------------
-- TÉRMINOS TÉCNICOS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS technical_terms (
    id              BIGSERIAL PRIMARY KEY,
    term            TEXT NOT NULL,
    normalized      TEXT NOT NULL,
    definition_sutra TEXT REFERENCES sutras(id) ON DELETE SET NULL,
    short_definition TEXT,
    UNIQUE (term)
);

CREATE INDEX IF NOT EXISTS idx_terms_normalized ON technical_terms (normalized);

-- ---------------------------------------------------------------------------
-- PRATYĀHĀRAS / DHĀTU-PĀṬHA / BASES NOMINALES / TABLAS
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pratyaharas (
    id              TEXT PRIMARY KEY,
    expansion       TEXT NOT NULL,
    defined_in      TEXT REFERENCES sutras(id) ON DELETE SET NULL,
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS dhatus (
    id              BIGSERIAL PRIMARY KEY,
    root            TEXT NOT NULL,
    gana            SMALLINT CHECK (gana IS NULL OR gana BETWEEN 1 AND 10),
    meaning         TEXT,
    markers         TEXT,
    raw_entry       TEXT,
    order_index     INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_dhatus_root ON dhatus (root);
CREATE INDEX IF NOT EXISTS idx_dhatus_gana ON dhatus (gana);

CREATE TABLE IF NOT EXISTS nominal_bases (
    id              BIGSERIAL PRIMARY KEY,
    base            TEXT NOT NULL,
    meaning         TEXT,
    notes           TEXT,
    order_index     INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_nominal_base ON nominal_bases (base);

CREATE TABLE IF NOT EXISTS embedded_tables (
    id              BIGSERIAL PRIMARY KEY,
    sutra_id        TEXT REFERENCES sutras(id) ON DELETE CASCADE,
    annex_type      TEXT,
    caption         TEXT,
    table_data      JSONB NOT NULL,
    order_index     INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_tables_sutra ON embedded_tables (sutra_id);

-- ---------------------------------------------------------------------------
-- AUDITORÍA
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id              BIGSERIAL PRIMARY KEY,
    source_file     TEXT NOT NULL,
    source_hash     TEXT NOT NULL,
    started_at      TIMESTAMPTZ NOT NULL,
    finished_at     TIMESTAMPTZ,
    sutras_loaded   INTEGER,
    notes_loaded    INTEGER,
    cross_refs_loaded INTEGER,
    status          TEXT,
    report          JSONB
);

-- ---------------------------------------------------------------------------
-- Trigger updated_at
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_sutras_updated_at ON sutras;
CREATE TRIGGER trg_sutras_updated_at
    BEFORE UPDATE ON sutras
    FOR EACH ROW
    EXECUTE PROCEDURE set_updated_at();