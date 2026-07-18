# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Web app for tracking sourdough starters and recipes. Runs locally/homelab. Privacy-first — no external cloud calls except Ollama (local).

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
docker compose up -d          # start all services
docker compose down           # stop
docker compose logs -f api    # tail backend logs
```

## Architecture

### Backend (`backend/`)
- `app/main.py` — FastAPI app, mounts routers, configures CORS
- `app/models/` — SQLAlchemy models: `Starter`, `Feeding`, `Recipe`, `Timer`
- `app/routers/` — one file per domain: `starters.py`, `recipes.py`, `timers.py`, `ollama.py`
- `app/db.py` — SQLite engine + session dependency (`get_db`)
- `app/ollama.py` — Ollama client: sends recipe text to local LLM, parses structured response

### Frontend (`frontend/src/`)
- `views/` — page-level components: `StartersView`, `RecipeView`, `TimerView`
- `components/` — reusable UI: `StarterCard`, `FeedingLog`, `RecipeImporter`, `TimerWidget`
- `stores/` — Pinia stores: `starters.ts`, `recipes.ts`, `timers.ts`
- `api/` — typed fetch wrappers matching backend routes

### Ollama Integration
Ollama runs as separate service (host or Docker). Backend calls `http://ollama:11434` (Docker) or `http://localhost:11434` (dev). Recipe import flow: user pastes raw text → `/api/recipes/import` → backend sends to Ollama with structured prompt → returns parsed `Recipe` JSON → user confirms and saves.

### Data Model (key relationships)
- `Starter` has many `Feeding` (feeding log per starter)
- `Recipe` has many `RecipeStep` (ordered steps with optional timer durations)
- `Timer` belongs to optional `RecipeStep`, tracks active countdowns

### Multi-Starter Design
All data scoped to `starter_id`. Starters have user-defined names. No auth — single-user homelab app.

## Environment Variables

```env
# backend/.env
DATABASE_URL=sqlite:///./sourdough.db
OLLAMA_BASE_URL=http://100.113.255.94:11434
OLLAMA_MODEL=llama3
```

## Docker Compose Services
- `api` — FastAPI backend
- `frontend` — Vue static files via nginx
- `ollama` — optional; can point to host Ollama instead
