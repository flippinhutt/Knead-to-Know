"""Ollama HTTP client. All functions read base_url/model from resolved_config()."""

import json
from collections.abc import AsyncIterator

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.setting import Setting


def resolved_config(db: Session) -> dict[str, str]:
    """Return effective ollama config: DB overrides take precedence over .env."""
    rows = db.query(Setting).filter(Setting.key.in_(["ollama_base_url", "ollama_model"])).all()
    overrides = {r.key: r.value for r in rows}
    return {
        "ollama_base_url": overrides.get("ollama_base_url", settings.ollama_base_url),
        "ollama_model": overrides.get("ollama_model", settings.ollama_model),
    }


async def list_models(base_url: str) -> list[dict]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{base_url}/api/tags", timeout=10.0)
        r.raise_for_status()
        return r.json().get("models", [])


async def pull_model(base_url: str, model_name: str) -> AsyncIterator[str]:
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{base_url}/api/pull",
            json={"name": model_name},
            timeout=300.0,
        ) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if line:
                    yield line


SYSTEM_PROMPT = """\
You are a friendly but precise sourdough baking coach inside a sourdough tracking app.

Audience: intermediate home bakers who understand basic sourdough concepts but want help \
troubleshooting, planning, and tweaking recipes. They use this app to store recipes, track \
feedings, monitor bulk fermentation, schedule bakes, and log results.

Persona and style:
- Be concise, practical, and specific.
- Prefer concrete numbers and ranges over vague advice.
- Avoid fluff and small talk. One short intro sentence is fine, but most of the response \
should be actionable guidance.
- When tradeoffs exist, briefly compare options and then give a clear recommendation.

Knowledge and boundaries:
- Focus on sourdough bread, levain, starter maintenance, fermentation, shaping, proofing, \
baking, and schedule planning.
- Say "I'm not sure" rather than guessing, especially about food safety.
- Do not give medical or health advice. For allergies or health conditions, tell the user to \
consult a professional.

Response guidelines:
- If the user asks a narrow question, answer directly and briefly.
- If the user is troubleshooting (e.g. "crumb is gummy", "loaf didn't rise"): ask at most 1-2 \
clarifying questions if truly needed, then offer likely causes and a concrete plan for the \
next bake.
- For schedule planning, propose an explicit timeline with clock times relative to "now" or \
the user's requested bake time.
- Use bullet points for multi-step plans.
- Avoid code blocks unless the user explicitly asks for one (e.g. baker's math).

You are allowed to suggest changes to: hydration, levain percentage, salt percentage, bulk \
and proof times and temperatures, shaping and scoring approach, oven setup (steam, Dutch oven \
vs. stone/steel). You only suggest changes — never claim to have modified stored data.\
"""

RECIPE_SYSTEM_PROMPT = """\
You are a sourdough recipe parser. You extract structured data from recipe text with \
precision. You never invent quantities, times, or temperatures not present in the source.\
"""

RECIPE_PROMPT = """\
You are a sourdough recipe parser. Convert messy, free-form recipe text into JSON \
matching EXACTLY this schema. Return ONLY valid JSON, no explanation, no markdown fences.

Schema:
{{
  "name": "string",
  "description": "string or null",
  "ingredients": [
    {{"order": 1, "name": "string", "amount": "string or null"}}
  ],
  "steps": [
    {{"order": 1, "title": "string or null", "description": "string", "duration_minutes": number_or_null}}
  ]
}}

Rules:
- If a field is unknown or not mentioned, use null (or an empty array for lists). Never invent \
quantities, times, or temperatures that aren't in the source text.
- "amount" is free text combining quantity and unit as written (e.g. "500g", "2 tsp", "1/4 cup"). \
For ranges like "2-3 hours" elsewhere in the text, use the midpoint (e.g. "2.5 hours") rather than \
the range.
- Ingredients that are sourdough starter, levain, or a pre-ferment should have that reflected in \
"name" (e.g. "active starter", "levain") rather than dropped or renamed.
- Lines starting with "## " are section headings from the source page. When a heading is \
immediately followed by body text before the next heading, treat the heading as that step's \
"title" and the body text as its "description". Steps without a heading get "title": null.
- Fold timing/temperature detail (autolyse, bulk fermentation, proof, bake) into the relevant \
step's "description" text rather than dropping it — there is no separate field for it.
- If the input text is not a recipe at all, return "name": "", "description": null, \
"ingredients": [], "steps": [].

Recipe:
{raw_text}
"""


async def chat(base_url: str, model: str, messages: list[dict]) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{base_url}/api/chat",
            json={
                "model": model,
                "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
                "stream": False,
                "options": {"temperature": 0.5},
            },
            timeout=120.0,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]


RECIPE_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "description": {"type": ["string", "null"]},
        "ingredients": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "order": {"type": "integer"},
                    "name": {"type": "string"},
                    "amount": {"type": ["string", "null"]},
                },
                "required": ["order", "name"],
            },
        },
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "order": {"type": "integer"},
                    "title": {"type": ["string", "null"]},
                    "description": {"type": "string"},
                    "duration_minutes": {"type": ["integer", "null"]},
                },
                "required": ["order", "description"],
            },
        },
    },
    "required": ["name", "steps"],
}


async def import_recipe(base_url: str, model: str, raw_text: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{base_url}/api/generate",
            json={
                "model": model,
                "system": RECIPE_SYSTEM_PROMPT,
                "prompt": RECIPE_PROMPT.format(raw_text=raw_text),
                "format": RECIPE_JSON_SCHEMA,
                "stream": False,
                "options": {"temperature": 0.1},
            },
            timeout=120.0,
        )
        r.raise_for_status()
        response_text = r.json()["response"]
        # Strip markdown code fences if present
        clean = response_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Model returned invalid JSON: {clean[:500]!r}") from exc
