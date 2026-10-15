/**
 * Cliente de la API FastAPI (solo lectura).
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...init?.headers,
    },
    // En desarrollo, revalidar con frecuencia; en prod se puede cachear
    next: { revalidate: 60 },
  });
  if (!res.ok) {
    if (res.status === 404) {
      throw new Error("NOT_FOUND");
    }
    throw new Error(`API ${res.status}: ${await res.text()}`);
  }
  return res.json() as Promise<T>;
}

/* ---------- Tipos ---------- */

export type Note = {
  id: number;
  note_number: number | null;
  content: string;
  note_type: string | null;
  order_index: number;
};

export type CrossReference = {
  id: number;
  to_sutra_ref: string;
  reference_text: string | null;
  ref_type: string | null;
  order_index: number;
};

export type Sutra = {
  id: string;
  adhyaya: number;
  pada: number;
  number: number;
  sanskrit: string;
  translation: string;
  order_index: number;
  has_tables: boolean;
  notes: Note[];
  cross_references: CrossReference[];
};

export type SutraListItem = {
  id: string;
  adhyaya: number;
  pada: number;
  number: number;
  sanskrit: string;
  translation_preview: string;
  order_index: number;
  notes_count: number;
};

export type SutraListResponse = {
  items: SutraListItem[];
  total: number;
  adhyaya: number | null;
  pada: number | null;
};

export type SearchResultItem = {
  id: string;
  adhyaya: number;
  pada: number;
  number: number;
  sanskrit: string;
  translation_preview: string;
  match_in: string;
};

export type SearchResponse = {
  query: string;
  items: SearchResultItem[];
  total: number;
};

export type Pratyahara = {
  id: string;
  expansion: string;
  defined_in: string | null;
  notes: string | null;
  order_index?: number;
  definition_full?: string | null;
};

export type PratyaharaSutra = {
  id: number;
  order_index: number;
  sutra_text: string;
  definition: string | null;
  generated_siglas: string | null;
};

export type Dhatu = {
  id: number;
  root: string;
  gana: number | null;
  meaning: string | null;
  markers: string | null;
  order_index: number;
  group_label?: string | null;
  section_major?: string | null;
  entry_number?: number | null;
  detail?: string | null;
};

export type NominalBase = {
  id: number;
  base: string;
  meaning: string | null;
  notes: string | null;
  order_index: number;
  group_name?: string | null;
  sutra_ref?: string | null;
  item_number?: number | null;
};

/* ---------- Llamadas ---------- */

export function getSutra(id: string) {
  return apiGet<Sutra>(`/sutras/${encodeURIComponent(id)}`);
}

export function listSutras(params: {
  adhyaya?: number;
  pada?: number;
  limit?: number;
  offset?: number;
}) {
  const q = new URLSearchParams();
  if (params.adhyaya != null) q.set("adhyaya", String(params.adhyaya));
  if (params.pada != null) q.set("pada", String(params.pada));
  if (params.limit != null) q.set("limit", String(params.limit));
  if (params.offset != null) q.set("offset", String(params.offset));
  const qs = q.toString();
  return apiGet<SutraListResponse>(`/sutras${qs ? `?${qs}` : ""}`);
}

export function search(q: string, limit = 30, offset = 0) {
  const params = new URLSearchParams({
    q,
    limit: String(limit),
    offset: String(offset),
  });
  return apiGet<SearchResponse>(`/search?${params}`);
}

export function listPratyaharas() {
  return apiGet<Pratyahara[]>("/annexes/pratyaharas");
}

export function listDhatus(params?: {
  gana?: number;
  limit?: number;
  offset?: number;
}) {
  const q = new URLSearchParams();
  if (params?.gana != null) q.set("gana", String(params.gana));
  if (params?.limit != null) q.set("limit", String(params.limit));
  if (params?.offset != null) q.set("offset", String(params.offset));
  const qs = q.toString();
  return apiGet<{ items: Dhatu[]; total: number; gana: number | null }>(
    `/annexes/dhatus${qs ? `?${qs}` : ""}`
  );
}

export function listNominalBases(params?: { limit?: number; offset?: number }) {
  const q = new URLSearchParams();
  if (params?.limit != null) q.set("limit", String(params.limit));
  if (params?.offset != null) q.set("offset", String(params.offset));
  const qs = q.toString();
  return apiGet<{ items: NominalBase[]; total: number }>(
    `/annexes/nominal-bases${qs ? `?${qs}` : ""}`
  );
}

export function health() {
  return apiGet<{ status: string; database: string }>("/health");
}
