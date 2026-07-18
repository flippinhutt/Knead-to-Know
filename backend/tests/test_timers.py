def test_create_and_list_timer(client):
    r = client.post("/api/timers/", json={"name": "Bulk Ferment", "duration_minutes": 240})
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Bulk Ferment"
    assert data["is_active"] is False

    r2 = client.get("/api/timers/")
    assert len(r2.json()) == 1


def test_start_timer(client):
    timer = client.post("/api/timers/", json={"name": "Proof", "duration_minutes": 60}).json()
    r = client.post(f"/api/timers/{timer['id']}/start")
    assert r.status_code == 200
    data = r.json()
    assert data["is_active"] is True
    assert data["started_at"] is not None
    assert data["ends_at"] is not None


def test_stop_timer(client):
    timer = client.post("/api/timers/", json={"name": "Proof", "duration_minutes": 60}).json()
    client.post(f"/api/timers/{timer['id']}/start")
    r = client.post(f"/api/timers/{timer['id']}/stop")
    assert r.status_code == 200
    assert r.json()["is_active"] is False


def test_delete_timer(client):
    timer = client.post("/api/timers/", json={"name": "Temp", "duration_minutes": 10}).json()
    r = client.delete(f"/api/timers/{timer['id']}")
    assert r.status_code == 204
