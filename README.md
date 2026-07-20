# Knead to Know

Sourdough starter tracker — log feedings, bakes, recipes, and timers. Runs locally/homelab. No external cloud. LLM features use [Ollama](https://ollama.com) (local).

See [docs/USER_GUIDE.md](docs/USER_GUIDE.md) for a walkthrough of daily use.

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + SQLAlchemy + SQLite |
| Frontend | Vue 3 + TypeScript + Pinia |
| LLM | Ollama (local, external to containers) |
| Deploy | Docker Compose |

## Features

- **Starters** — track multiple starters, log feedings (flour/water/starter grams, rise height, ambient temp, flour type/brand, notes), feeding reminders, SVG rise chart, archive/restore
- **Recipes** — create recipes with ordered steps (optional title + description); import raw text or URL via Ollama (paste recipe text, or fetch a URL — JSON-LD parsed directly, else page HTML flattened with headings tagged so Ollama maps `h1`/`h2`/`h3` to step title and following text to step description; if source has both a short summary and a detailed step section, parser uses the detailed section only → review + confirm → saved); detail view with step check-off; scaling (weights + durations update)
- **Bakes** — log bakes linked to starter + recipe; outcome, oven temp, custom date, tags
- **Timers** — countdown timers, optionally linked to recipe steps; sound + browser notification when a timer finishes
- **Baker Chat** — multi-turn sourdough Q&A via Ollama, tuned for friendly/concise advice (separate prompt + temperature from recipe import)
- **Calculators** — Hydration tab (flour + hydration % + starter → added water); Unit Converter tab (grams ↔ cups per ingredient)
- **Units** — weight (g/oz/cup) and temperature (°F/°C) settings; stored as g/°F, displayed per preference
- **Dark mode** — persisted to localStorage
- **Backup/Restore** — JSON export + import via Settings

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose v2
- [Ollama](https://ollama.com) running on the host (or reachable network instance) with at least one model pulled

```bash
ollama pull llama3   # or llama3.2, mistral, etc.
```

> **No authentication.** Designed for local/homelab use — no login, no user accounts. Do not expose publicly without adding auth at the network layer.

## Quick Start (Docker)

```bash
cp .env.example .env   # edit OLLAMA_BASE_URL if Ollama isn't on localhost

docker compose up -d

# App: http://localhost:3000
```

## Deploy Prebuilt Images

GitHub Actions builds and pushes images to GHCR on every push to `main`.

```bash
cp .env.example .env   # edit OLLAMA_BASE_URL if needed
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

Images: `ghcr.io/flippinhutt/knead-to-know-api`, `ghcr.io/flippinhutt/knead-to-know-frontend`

Packages default to private on GHCR — either make them public in package settings, or `docker login ghcr.io` on the deploy host first.

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `3000` | Host port for frontend |
| `OLLAMA_BASE_URL` | `http://host.docker.internal:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `llama3` | Default model for chat + import |

## Local Development

**Requires:** Python 3.10+, Node 18+

### Backend

```bash
cd backend
cp .env.example .env            # edit as needed
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload   # http://localhost:8000
pytest                          # run tests
pytest -x                       # stop on first failure
```

### Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
npm test           # vitest unit tests
npm run typecheck  # type check only
npm run build      # production build
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET/POST | `/api/starters/` | List / create starters |
| GET/PATCH/DELETE | `/api/starters/{id}` | Get / update / delete starter |
| GET/POST | `/api/starters/{id}/feedings` | List / add feedings |
| GET/POST | `/api/recipes/` | List / create recipes |
| GET/PATCH/DELETE | `/api/recipes/{id}` | Get / update / delete recipe |
| POST | `/api/recipes/import` | Import recipe text via Ollama |
| GET/POST | `/api/timers/` | List / create timers |
| GET/DELETE | `/api/timers/{id}` | Get / delete timer |
| GET/POST | `/api/bakes/` | List / create bakes |
| GET/PATCH/DELETE | `/api/bakes/{id}` | Get / update / delete bake |
| GET | `/api/export/` | Full JSON backup download |
| POST | `/api/import/` | Restore from JSON backup |
| GET/POST | `/api/ollama/config` | Get / set Ollama URL + model |
| GET | `/api/ollama/models` | List available Ollama models |
| POST | `/api/ollama/pull` | Pull a model |
| POST | `/api/ollama/chat` | Multi-turn chat |

Interactive docs (dev only): `http://localhost:8000/docs`

## Data Model

```
Starter
  ├── name, description, hydration_percent
  ├── feed_interval_hours  (feeding reminder interval)
  ├── archived             (soft delete)
  └── Feeding[]
        ├── flour_grams, water_grams, starter_grams
        ├── height_mm, ambient_temp_f
        └── flour_type, flour_brand, notes

Recipe
  ├── name, description, source, image_url
  ├── RecipeStep[]        (ordered, optional title, optional duration_minutes)
  └── RecipeIngredient[]  (ordered, name, optional amount)

Bake
  ├── starter_id (FK, optional)
  ├── recipe_id  (FK, optional)
  ├── baked_at, hydration_percent, oven_temp_f (stored °F)
  ├── outcome, notes
  └── tags  (comma-separated string)

Timer
  ├── name, duration_minutes
  ├── started_at, ends_at, is_active
  └── recipe_step_id (FK, optional)

Setting  (key/value, persists Ollama config across restarts)
```

## Migrations

`backend/app/migrate.py` runs on startup via `PRAGMA table_info` + `ALTER TABLE ADD COLUMN`. Safe to re-run — columns only added if missing. No migration tool required; just start the app.

## Docker Services

| Service | Description |
|---|---|
| `api` | FastAPI/uvicorn on port 8000 (internal); SQLite in named volume `db-data` |
| `frontend` | Vue build served by nginx on `${PORT:-3000}`; proxies `/api/*` → `api:8000` |

Ollama is external — not managed by Compose. Set `OLLAMA_BASE_URL` to point at your instance.

## Project Structure

```
sourdough/
├── backend/
│   ├── app/
│   │   ├── main.py          FastAPI app, router mounts, CORS, startup
│   │   ├── db.py            SQLite engine, session dependency
│   │   ├── migrate.py       Startup column migrations
│   │   ├── config.py        Settings (pydantic-settings)
│   │   ├── models/          SQLAlchemy models
│   │   ├── schemas/         Pydantic schemas
│   │   ├── routers/         One file per domain
│   │   └── services/        Ollama HTTP client (separate system prompts + temperature per call: recipe parser vs. baker chat)
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/           StartersView, RecipesView, RecipeDetailView, BakesView, etc.
│   │   ├── components/      StarterCard, FeedingLog, RecipeCard, etc.
│   │   ├── stores/          Pinia stores per domain + units + theme
│   │   ├── api/             Typed fetch wrappers
│   │   ├── router/          Vue Router routes
│   │   └── types/           Shared TypeScript interfaces
│   └── nginx.conf
├── docker-compose.yml
└── CLAUDE.md
```

## License

MIT
