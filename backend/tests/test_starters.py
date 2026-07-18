def test_list_starters_empty(client):
    r = client.get("/api/starters/")
    assert r.status_code == 200
    assert r.json() == []


def test_create_starter(client):
    r = client.post("/api/starters/", json={"name": "Rye Bob", "hydration_percent": 100.0})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Rye Bob"
    assert data["hydration_percent"] == 100.0
    assert data["id"] is not None


def test_get_starter(client):
    created = client.post("/api/starters/", json={"name": "Bubbles"}).json()
    r = client.get(f"/api/starters/{created['id']}")
    assert r.status_code == 200
    assert r.json()["name"] == "Bubbles"


def test_get_starter_not_found(client):
    r = client.get("/api/starters/999")
    assert r.status_code == 404


def test_update_starter(client):
    created = client.post("/api/starters/", json={"name": "Old Name"}).json()
    r = client.patch(f"/api/starters/{created['id']}", json={"name": "New Name"})
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"


def test_delete_starter(client):
    created = client.post("/api/starters/", json={"name": "Temp"}).json()
    r = client.delete(f"/api/starters/{created['id']}")
    assert r.status_code == 204
    assert client.get(f"/api/starters/{created['id']}").status_code == 404


def test_add_feeding(client):
    starter = client.post("/api/starters/", json={"name": "Levain"}).json()
    r = client.post(
        f"/api/starters/{starter['id']}/feedings",
        json={"flour_grams": 50, "water_grams": 50, "starter_grams": 10},
    )
    assert r.status_code == 201
    assert r.json()["flour_grams"] == 50


def test_list_feedings(client):
    starter = client.post("/api/starters/", json={"name": "Levain"}).json()
    client.post(f"/api/starters/{starter['id']}/feedings", json={"flour_grams": 50})
    client.post(f"/api/starters/{starter['id']}/feedings", json={"flour_grams": 75})
    r = client.get(f"/api/starters/{starter['id']}/feedings")
    assert r.status_code == 200
    assert len(r.json()) == 2
