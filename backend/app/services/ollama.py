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
You are an expert sourdough baker with deep knowledge of fermentation, \
hydration ratios, starter maintenance, crumb structure, and baking schedules. \
You help bakers understand and execute sourdough recipes with precision. \
When parsing recipes, you identify timing, temperatures, and techniques accurately.\
"""

RECIPE_PROMPT = """\
Parse this sourdough recipe into JSON. Return ONLY valid JSON, no explanation.

Lines starting with "## " are section headings from the source page. When a heading is \
immediately followed by body text before the next heading, treat the heading as that \
step's "title" and the body text as its "description". Steps without a heading get \
"title": null.

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
                "system": SYSTEM_PROMPT,
                "prompt": RECIPE_PROMPT.format(raw_text=raw_text),
                "format": RECIPE_JSON_SCHEMA,
                "stream": False,
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
