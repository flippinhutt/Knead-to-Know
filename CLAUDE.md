# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Knead to Know** — web app for tracking sourdough starters, feedings, recipes, and bakes. Runs locally/homelab. Privacy-first — no external cloud calls except Ollama (local LLM).

**Stack:** FastAPI (Python) · Vue 3 (TypeScript) · SQLite · Docker Compose · Ollama (local LLM)

## Commands

### Backend (FastAPI)
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload          # dev server (port 8000)
pytest                                  # all tests
pytest tests/test_starters.py          # single test file
pytest -x                              # stop on first failure
```

### Frontend (Vue 3)
```bash
cd frontend
npm install
npm run dev        # dev server (port 5173)
npm run build      # production build
npm run typecheck  # type check only
npm test           # vitest unit tests
```

### Docker (full stack)
```bash
docker compose up -d          # start all services (app on port 3000)
docker compose down           # stop
docker compose logs -f api    # tail backend logs
```

## Architecture

### Backend (`backend/app/`)
- `main.py` — FastAPI app, mounts routers, runs startup migrations, configures CORS
- `migrate.py` — SQLite ALTER TABLE migrations run on startup (safe to re-run)
- `models/` — SQLAlchemy models: `Starter`, `Feeding`, `Recipe`, `RecipeStep`, `Timer`, `Bake`, `Setting`
- `schemas/` — Pydantic schemas per domain
- `routers/` — one file per domain:
  - `starters.py` — CRUD + feedings; `?show_archived=true` to include archived
  - `recipes.py` — CRUD + Ollama import
  - `timers.py` — active countdown timers
  - `bakes.py` — bake log (links starter + recipe)
  - `ollama.py` — config, model list/pull, `/chat` endpoint
  - `export_data.py` — GET `/api/export/` returns full JSON backup (download)
  - `import_data.py` — POST `/api/import/` restores from backup JSON, remaps IDs
- `services/ollama.py` — Ollama HTTP client; sourdough expert system prompt on all requests
- `db.py` — SQLite engine + `get_db` session dependency

### Frontend (`frontend/src/`)
- `views/` — `StartersView`, `RecipesView`, `TimersView`, `BakesView`, `ChatView`, `HydrationView`, `SettingsView`
- `components/` — `StarterCard`, `FeedingLog`, `RecipeCard`, `RecipeImporter`, `TimerWidget`, `BakeCard`
- `stores/` — `starters.ts`, `recipes.ts`, `timers.ts`, `bakes.ts`, `ollama.ts`, `units.ts` (weight + temp unit, localStorage-persisted), `theme.ts`
- `api/` — typed fetch wrappers; all requests go through `/api` prefix (proxied by nginx in Docker)

### Ollama Integration
Ollama runs on host or as separate Docker service. All requests include a sourdough expert system prompt.
- **Recipe import:** paste raw text → `/api/recipes/import` → Ollama parses → user confirms → saved
- **Baker chat:** `/chat` view, multi-turn conversation, full message history sent each request

### Data Model
- `Starter` → many `Feeding` (flour/water/starter grams, height_mm, ambient_temp_f, flour_type, flour_brand, notes)
- `Starter` fields: `feed_interval_hours` (reminder), `archived` (soft delete)
- `Recipe` → many `RecipeStep` (ordered, optional duration_minutes)
- `Bake` → optional FK to `Starter` and `Recipe`; records baked_at (user-settable date), hydration, oven temp (stored °F), outcome, tags (comma-sep string), notes
- `Timer` → optional FK to `RecipeStep`
- `Setting` — key/value store for Ollama URL/model overrides (survives restarts)

### DB Migrations
New columns are added via `app/migrate.py` at startup using `PRAGMA table_info` + `ALTER TABLE ADD COLUMN`. Safe for existing installs — columns only added if missing.

Migrations tracked:
- `feedings`: `height_mm`, `ambient_temp_f`, `flour_type`, `flour_brand`
- `starters`: `feed_interval_hours`, `archived`
- `bakes`: `tags`

## Features

| Feature | Location |
|---|---|
| Starter tracking + feeding log | StartersView / StarterCard |
| Feeding reminders (interval badge) | StarterCard — "Feed me!" badge when overdue |
| Rise chart (height over time) | FeedingLog — SVG sparkline from `height_mm` readings |
| Starter archive / restore | StarterCard archive button; StartersView "Show archived" toggle |
| Recipe import via Ollama | RecipesView → Import via Ollama |
| Recipe step check-off | RecipeCard — click step to mark done |
| Recipe scaling | RecipeCard — scale × input, durations update, weight banner shown |
| Timers | TimersView |
| Bake log | BakesView — links starter + recipe, records outcome, bake date, tags |
| Bake date | BakesView — datetime-local picker; defaults to server time if omitted |
| Bake tags | BakesView — comma-sep tags shown as pills on BakeCard |
| Flour type + brand on feedings | StarterCard — datalist suggestions for type; freetext brand; displayed in FeedingLog |
| Baker chat (Ollama) | ChatView — multi-turn sourdough expert Q&A |
| Hydration calculator | HydrationView — flour/hydration/starter → added water |
| Unit setting (g/oz/cup) | Settings → Units (weight); applies to all weight inputs + feeding display |
| Temperature unit (°F/°C) | Settings → Units (temp); all temp inputs + display convert; stored as °F |
| Dark mode | ◑ toggle in nav, persists to localStorage |
| Data export | Settings → Download Backup (JSON) |
| Data import | Settings → Import Backup (file picker) |

## Environment Variables

```env
# backend/.env (local dev)
DATABASE_URL=sqlite:///./sourdough.db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

```env
# root .env (Docker override)
PORT=3000                              # host port for frontend (default 3000)
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
```

## Docker Compose Services
- `api` — FastAPI/uvicorn backend; SQLite stored in named volume `db-data`
- `frontend` — Vue build served by nginx; proxies `/api/*` → `api:8000`
- Ollama: external (set `OLLAMA_BASE_URL` to point to host or separate instance)
