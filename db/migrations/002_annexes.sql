-- =============================================================================
-- Ampliar tablas de anexos (migración 002)
-- =============================================================================

-- DHĀTUS / primitivos
ALTER TABLE dhatus ADD COLUMN IF NOT EXISTS group_label   TEXT;
ALTER TABLE dhatus ADD COLUMN IF NOT EXISTS section_major TEXT;
ALTER TABLE dhatus ADD COLUMN IF NOT EXISTS subsection    TEXT;
ALTER TABLE dhatus ADD COLUMN IF NOT EXISTS level4        TEXT;
ALTER TABLE dhatus ADD COLUMN IF NOT EXISTS level5        TEXT;
ALTER TABLE dhatus ADD COLUMN IF NOT EXISTS entry_number  INTEGER;
ALTER TABLE dhatus ADD COLUMN IF NOT EXISTS detail        TEXT;

CREATE INDEX IF NOT EXISTS idx_dhatus_group ON dhatus (group_label);
CREATE INDEX IF NOT EXISTS idx_dhatus_entry ON dhatus (entry_number);

-- BASES NOMINALES
ALTER TABLE nominal_bases ADD COLUMN IF NOT EXISTS group_name   TEXT;
ALTER TABLE nominal_bases ADD COLUMN IF NOT EXISTS sutra_ref    TEXT;
ALTER TABLE nominal_bases ADD COLUMN IF NOT EXISTS item_number  INTEGER;

CREATE INDEX IF NOT EXISTS idx_nominal_group ON nominal_bases (group_name);

-- PRATYĀHĀRA-SŪTRAS (los 14 Śiva-sūtras)
CREATE TABLE IF NOT EXISTS pratyahara_sutras (
    id              BIGSERIAL PRIMARY KEY,
    order_index     INTEGER NOT NULL DEFAULT 0,
    sutra_text      TEXT NOT NULL,          -- aiuṆ, ṛḷK, …
    definition      TEXT,
    generated_siglas TEXT                   -- aṆ¹, aK, iK, …
);

-- SIGLAS: se cargan en pratyaharas (id = sigla)
-- Añadimos order_index si no existe vía columna notes ya presente
ALTER TABLE pratyaharas ADD COLUMN IF NOT EXISTS order_index INTEGER DEFAULT 0;
ALTER TABLE pratyaharas ADD COLUMN IF NOT EXISTS definition_full TEXT;