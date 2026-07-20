# User Guide — Knead to Know

Step-by-step guide for daily use. For setup, see [README.md](../README.md).

## Starters

### Add a starter
1. Starters tab → **New Starter**.
2. Enter name, description, hydration %.
3. Optional: set **feed interval** (hours) — starter shows "Feed me!" badge once overdue.

### Log a feeding
1. Open starter card → **Log Feeding**.
2. Enter flour grams, water grams, starter grams.
3. Optional: rise height (mm), ambient temp, flour type/brand, notes.
4. Save — feeding appears in the log; rise readings build the SVG rise chart over time.

### Archive / restore
- Archive button on starter card soft-deletes it (hidden from default list).
- Toggle **Show archived** on Starters view to see and restore archived starters.

## Recipes

### Create manually
1. Recipes tab → **New Recipe**.
2. Add name/description, then add steps in order (title + description optional, duration in minutes optional).

### Import via Ollama
1. Recipes tab → **Import via Ollama**.
2. Paste raw recipe text, or paste a URL.
   - URL fetch tries JSON-LD `Recipe` schema first.
   - Otherwise the page is flattened to text with `h1`/`h2`/`h3` lines tagged, so Ollama maps headings → step titles and following text → step descriptions.
3. Review the parsed steps, edit anything wrong, then confirm to save.

### Use a recipe
- Open a recipe to view its detail page.
- Click a step to check it off while baking.
- Use the **scale ×** input to scale weights and durations (e.g. 1.5× a full recipe) — a weight banner shows the scaled totals.

## Bakes

1. Bakes tab → **New Bake**.
2. Link a starter and/or recipe (both optional).
3. Set bake date (defaults to now), hydration %, oven temp, outcome, tags (comma-separated), notes.
4. Bake card shows tags as pills.

## Timers

1. Timers tab → **New Timer**.
2. Set name + duration; optionally link to a recipe step.
3. Countdown runs live; timer clears when it hits zero or is deleted.

## Baker Chat

- Chat tab — multi-turn Q&A with a sourdough-expert system prompt via Ollama.
- Full conversation history is sent with each message, so context carries across turns.

## Calculators

- **Hydration tab** — enter flour weight, target hydration %, and starter hydration/amount to get the water to add.
- **Unit Converter tab** — convert grams ↔ cups for a given ingredient.

## Settings

- **Units** — switch weight display (g/oz/cup) and temperature display (°F/°C). Values are stored internally as grams/°F regardless of display setting.
- **Dark mode** — ◑ toggle in the nav bar, persists across sessions.
- **Backup** — **Download Backup** exports full data as JSON.
- **Restore** — **Import Backup** restores from a previously exported JSON file (remaps IDs; does not merge — review before importing over existing data).
- **Ollama** — set Ollama base URL and default model; pull new models from the configured instance.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Import via Ollama fails | Ollama unreachable, or model not pulled | Check `OLLAMA_BASE_URL` in Settings; run `ollama pull <model>` |
| Chat gives no response | Ollama service down | Confirm Ollama running on host: `ollama list` |
| Feeding reminder never shows | No `feed_interval_hours` set on starter | Edit starter, set feed interval |
| Import backup rejects file | JSON malformed or from unrelated app | Re-export from Knead to Know and retry |
