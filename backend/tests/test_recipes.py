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
