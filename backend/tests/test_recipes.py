import json

import pytest

from app.routers.recipes import _extract_recipe_from_json_ld


# ---------------------------------------------------------------------------
# JSON-LD extraction unit tests
# ---------------------------------------------------------------------------

_JSON_LD_HTML = """
<html><head>
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Recipe",
  "name": "Classic Sourdough",
  "description": "A simple loaf",
  "recipeInstructions": [
    {"@type": "HowToStep", "text": "Mix flour and water"},
    {"@type": "HowToStep", "text": "Fold dough every 30 minutes"}
  ]
}
</script>
</head><body>Ignore this text</body></html>
"""

_MALFORMED_JSON_LD_HTML = """
<html><head>
<script type="application/ld+json">{ not valid json }</script>
</head><body>Fallback text here</body></html>
"""

_ARRAY_JSON_LD_HTML = """
<html><head>
<script type="application/ld+json">
[{"@type": "WebPage", "name": "Page"}, {"@type": "Recipe", "name": "Rye Loaf", "recipeInstructions": ["Autolyse", "Shape"]}]
</script>
</head></html>
"""


def test_json_ld_extracts_recipe_fields():
    result = _extract_recipe_from_json_ld(_JSON_LD_HTML)
    assert result is not None
    assert "Classic Sourdough" in result
    assert "A simple loaf" in result
    assert "Mix flour and water" in result
    assert "Fold dough every 30 minutes" in result


def test_json_ld_malformed_returns_none():
    result = _extract_recipe_from_json_ld(_MALFORMED_JSON_LD_HTML)
    assert result is None


def test_json_ld_array_finds_recipe():
    result = _extract_recipe_from_json_ld(_ARRAY_JSON_LD_HTML)
    assert result is not None
    assert "Rye Loaf" in result
    assert "Autolyse" in result


def test_json_ld_no_recipe_type_returns_none():
    html = '<script type="application/ld+json">{"@type": "WebPage"}</script>'
    assert _extract_recipe_from_json_ld(html) is None


def test_import_url_uses_json_ld_when_present(client, monkeypatch):
    captured: list[str] = []

    async def _capture_import(base_url, model, raw_text):
        captured.append(raw_text)
        return _FAKE_PARSED

    monkeypatch.setattr("app.routers.recipes.ollama_service.resolved_config", lambda db: _FAKE_CONFIG)
    monkeypatch.setattr("app.routers.recipes.ollama_service.import_recipe", _capture_import)

    class _JsonLdClient:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *a): pass
        async def get(self, *a, **kw):
            class R:
                text = _JSON_LD_HTML
                def raise_for_status(self): pass
            return R()

    monkeypatch.setattr("app.routers.recipes.httpx.AsyncClient", _JsonLdClient)

    r = client.post("/api/recipes/import", json={"url": "https://example.com/sourdough"})
    assert r.status_code == 200
    assert "Classic Sourdough" in captured[0]
    assert "Ignore this text" not in captured[0]


# ---------------------------------------------------------------------------
# /import tests
# ---------------------------------------------------------------------------

_FAKE_PARSED = {
    "name": "Test Loaf",
    "description": "A test",
    "steps": [{"order": 1, "description": "Mix", "duration_minutes": None}],
}

_FAKE_CONFIG = {"ollama_base_url": "http://localhost:11434", "ollama_model": "llama3"}


async def _mock_import_recipe(base_url, model, raw_text):
    return _FAKE_PARSED


class _MockResponse:
    text = "<html><body>Sourdough recipe text here</body></html>"

    def raise_for_status(self):
        pass


class _MockAsyncClient:
    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get(self, *args, **kwargs):
        return _MockResponse()


class _FailingAsyncClient:
    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def get(self, *args, **kwargs):
        raise Exception("Connection refused")


def test_import_raw_text(client, monkeypatch):
    monkeypatch.setattr("app.routers.recipes.ollama_service.resolved_config", lambda db: _FAKE_CONFIG)
    monkeypatch.setattr("app.routers.recipes.ollama_service.import_recipe", _mock_import_recipe)

    r = client.post("/api/recipes/import", json={"raw_text": "Mix flour and water. Bake."})

    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "Test Loaf"
    assert isinstance(data["steps"], list)
    assert data["steps"][0]["order"] == 1


def test_import_empty_body_returns_422(client):
    r = client.post("/api/recipes/import", json={})
    assert r.status_code == 422


def test_import_url_fetches_and_parses(client, monkeypatch):
    monkeypatch.setattr("app.routers.recipes.ollama_service.resolved_config", lambda db: _FAKE_CONFIG)
    monkeypatch.setattr("app.routers.recipes.ollama_service.import_recipe", _mock_import_recipe)
    monkeypatch.setattr("app.routers.recipes.httpx.AsyncClient", _MockAsyncClient)

    r = client.post("/api/recipes/import", json={"url": "https://example.com/recipe"})

    assert r.status_code == 200
    assert r.json()["name"] == "Test Loaf"


def test_import_bad_url_returns_400(client, monkeypatch):
    monkeypatch.setattr("app.routers.recipes.httpx.AsyncClient", _FailingAsyncClient)

    r = client.post("/api/recipes/import", json={"url": "https://bad.example.invalid/recipe"})

    assert r.status_code == 400
    assert "Failed to fetch URL" in r.json()["detail"]


# ---------------------------------------------------------------------------
# Existing tests
# ---------------------------------------------------------------------------

def test_list_recipes_empty(client):
    r = client.get("/api/recipes/")
    assert r.status_code == 200
    assert r.json() == []


def test_create_recipe(client):
    payload = {
        "name": "Basic Country Loaf",
        "description": "Simple 75% hydration loaf",
        "steps": [
            {"order": 1, "description": "Autolyse flour and water", "duration_minutes": 30},
            {"order": 2, "description": "Add levain and salt"},
        ],
    }
    r = client.post("/api/recipes/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Basic Country Loaf"
    assert len(data["steps"]) == 2
    assert data["steps"][0]["duration_minutes"] == 30


def test_get_recipe_not_found(client):
    r = client.get("/api/recipes/999")
    assert r.status_code == 404


def test_update_recipe(client):
    created = client.post("/api/recipes/", json={"name": "Old"}).json()
    r = client.patch(f"/api/recipes/{created['id']}", json={"name": "Updated"})
    assert r.status_code == 200
    assert r.json()["name"] == "Updated"


def test_delete_recipe(client):
    created = client.post("/api/recipes/", json={"name": "Temp"}).json()
    r = client.delete(f"/api/recipes/{created['id']}")
    assert r.status_code == 204
    assert client.get(f"/api/recipes/{created['id']}").status_code == 404
