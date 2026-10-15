# Frontend — Aṣṭādhyāyī (Next.js)

UI de lectura para la gramática de Pāṇini en español.

## Requisitos

- Node 18+
- API FastAPI en marcha (`http://localhost:8000`)

## Arranque

```bash
cd web
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

npm install
npm run dev
```

Abre http://localhost:3000

## Páginas

| Ruta | Descripción |
|------|-------------|
| `/` | Inicio + acceso por adhyāya |
| `/sutras?adhyaya=1&pada=2` | Listado filtrable |
| `/sutras/1.1.1` | Detalle (traducción, notas, refs) |
| `/search?q=guṇa` | Búsqueda |
| `/annexes/pratyaharas` | Siglas / pratyāhāras |
| `/annexes/dhatus` | Dhātu-pāṭha |
| `/annexes/nominal-bases` | Bases nominales |

## Diseño

- Paleta pergamino + azafrán (lectura cómoda, tono académico)
- Tipografía: Literata (serif) para sánscrito/títulos, Inter para UI
- Solo lectura; sin edición en cliente
