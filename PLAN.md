# Recipe Improvements Plan

## Tasks

### Task 1 — Auto-save source URL
**Status:** TODO  
**Scope:** 1 file, ~2 lines

When importing a recipe from a URL, save that URL in the recipe's `source` field.

**File:** `frontend/src/components/RecipeImporter.vue`  
**Change:** In `save()`, pass `source: url.value` when `mode === 'url'`

---

### Task 2 — Recipe step editing
**Status:** TODO  
**Scope:** 5 files

No way to fix bad Ollama parse without deleting + reimporting. Add inline step editing.

**Backend:**
- `backend/app/schemas/recipe.py` — add `RecipeStepReplace` schema (list of steps, no ID required)
- `backend/app/routers/recipes.py` — add `PUT /api/recipes/{id}/steps` endpoint that replaces all steps for a recipe atomically (delete existing, insert new)

**Frontend:**
- `frontend/src/api/recipes.ts` — add `replaceSteps(id, steps[])` method → `PUT /recipes/{id}/steps`
- `frontend/src/stores/recipes.ts` — add `replaceSteps(id, steps[])` action, updates local state
- `frontend/src/components/RecipeCard.vue` — "Edit steps" button toggles inline form; each step has editable description + duration_minutes; Save calls `replaceSteps`

---

### Task 3 — Tests for /import endpoint
**Status:** TODO  
**Scope:** 1 file

`/api/recipes/import` has zero test coverage.

**File:** `backend/tests/test_recipes.py`

**Tests to add:**
1. `raw_text` path → 200, valid preview shape (mock `ollama_service.import_recipe`)
2. Empty body (no `raw_text`, no `url`) → 422
3. `url` field → fetches page, strips HTML, passes to Ollama → 200 (monkeypatch httpx.AsyncClient)
4. Bad/unreachable URL → 400

Mock target: `app.routers.recipes.ollama_service.import_recipe` (patch at import site)  
Mock httpx at: `app.routers.recipes.httpx.AsyncClient`

---

### Task 4 — JSON-LD extraction for URL imports
**Status:** TODO  
**Scope:** 1 file

Recipe sites (AllRecipes, King Arthur, Serious Eats, etc.) embed structured data as JSON-LD. Parsing that directly gives far better results than stripping HTML.

**File:** `backend/app/routers/recipes.py`

**Change:** Before running `_TextExtractor`, scan HTML for `<script type="application/ld+json">` tags. Parse each JSON blob; if `@type == "Recipe"` (or array containing one), extract:
- `name`
- `description`
- `recipeInstructions` (array of `HowToStep` or plain strings)

Format as plain text and pass to Ollama. Fall back to HTML strip if no valid Recipe JSON-LD found. Wrap JSON parse in `try/except` — malformed JSON-LD should not crash the import.

---

## Risks

- JSON-LD may be malformed or nested — wrap all parsing in try/except, fall back to HTML strip
- Step replace is atomic (delete all + insert new) — race condition possible with two tabs open; acceptable for homelab use
- httpx mock in tests must match `async with httpx.AsyncClient() as client:` context manager pattern

## Verification

- [ ] `pytest -x` passes after each task
- [ ] Task 1: import from URL → `recipe.source` populated
- [ ] Task 2: edit steps → reload page → steps persist
- [ ] Task 3: all new tests green, no mock leakage
- [ ] Task 4: import from King Arthur or AllRecipes URL → name + steps parse correctly

## Context

These improvements were identified after implementing URL recipe import (added in same session).
URL import PR: fetches page with httpx, strips HTML via stdlib `html.parser`, feeds to Ollama.
Stack: FastAPI + SQLAlchemy + SQLite backend, Vue 3 + Pinia frontend.
Backend tests use `pytest` with a `TestClient` fixture in `backend/tests/conftest.py`.
