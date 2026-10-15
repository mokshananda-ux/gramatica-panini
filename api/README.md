# API FastAPI – Gramática de Pāṇini (solo lectura)

## Requisitos

- Python 3.11+
- PostgreSQL con el esquema cargado (`db/migrations/001_initial.sql`)
- Datos cargados vía `pipeline/load.py`

## Instalación

```bash
cd api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tu DATABASE_URL
```

## Arranque

```bash
# Desde el directorio api/
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Documentación interactiva: http://localhost:8000/docs

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado de la API y de la BD |
| GET | `/sutras` | Listado (filtros: `adhyaya`, `pada`, `limit`, `offset`) |
| GET | `/sutras/{id}` | Detalle de un sūtra (notas + referencias) |
| GET | `/search?q=` | Búsqueda por texto o por id (`1.1.1`) |
| GET | `/annexes/pratyaharas` | Listado de pratyāhāras |
| GET | `/annexes/pratyaharas/{id}` | Detalle de un pratyāhāra |
| GET | `/annexes/dhatus` | Listado del Dhātu-pāṭha (`gana`, `limit`, `offset`) |
| GET | `/annexes/nominal-bases` | Listado de bases nominales |

## Ejemplos

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/sutras?adhyaya=1&pada=2&limit=10"
curl http://localhost:8000/sutras/1.2.1
curl "http://localhost:8000/search?q=guṇa"
curl "http://localhost:8000/search?q=1.1.1"
```
