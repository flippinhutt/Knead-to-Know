from unittest.mock import AsyncMock, patch

import pytest


def test_get_config_defaults(client):
    r = client.get("/api/ollama/config")
    assert r.status_code == 200
    data = r.json()
    assert "ollama_base_url" in data
    assert "ollama_model" in data


def test_update_config(client):
    r = client.patch(
        "/api/ollama/config",
        json={"ollama_model": "mistral", "ollama_base_url": "http://192.168.1.10:11434"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["ollama_model"] == "mistral"
    assert data["ollama_base_url"] == "http://192.168.1.10:11434"


def test_update_config_persists(client):
    client.patch("/api/ollama/config", json={"ollama_model": "phi3"})
    r = client.get("/api/ollama/config")
    assert r.json()["ollama_model"] == "phi3"


@pytest.mark.asyncio
async def test_list_models(client):
    mock_models = [{"name": "llama3", "size": 4000000000, "modified_at": "2024-01-01"}]
    with patch("app.services.ollama.list_models", new_callable=AsyncMock, return_value=mock_models):
        r = client.get("/api/ollama/models")
    assert r.status_code == 200
    assert r.json()[0]["name"] == "llama3"
