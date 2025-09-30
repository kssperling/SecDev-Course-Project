TOK = {"Authorization": "Bearer token-alice"}

def test_crud_flow(client):
    r = client.post(
        "/entries",
        json={
            "title": "Clean Architecture",
            "kind": "book",
            "link": None,
            "status": "planned",
        },
    )
    assert r.status_code == 200, r.text
    eid = r.json()["id"]

    r = client.get(f"/entries/{eid}")
    assert r.status_code == 200
    assert r.json()["title"] == "Clean Architecture"

    r = client.get("/entries")
    assert r.status_code == 200
    assert any(x["id"] == eid for x in r.json())

    r = client.get("/entries?status=planned")
    assert r.status_code == 200
    assert all(x["status"] == "planned" for x in r.json())

    r = client.put(f"/entries/{eid}", json={"status": "in_progress"})
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"

    r = client.delete(f"/entries/{eid}")
    assert r.status_code == 200


def test_validation(client):
    r = client.post(
        "/entries", json={"title": "", "kind": "book", "status": "planned"}
    )
    assert r.status_code == 422

    r = client.post(
        "/entries", json={"title": "Test", "kind": "invalid_kind", "status": "planned"}
    )
    assert r.status_code == 422


def test_partial_update(client):
    # Создаем запись
    r = client.post(
        "/entries",
        json={
            "title": "Original Title",
            "kind": "book",
            "status": "planned"
        },
    )
    eid = r.json()["id"]

    # Обновляем только статус
    r = client.put(f"/entries/{eid}", json={"status": "completed"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["title"] == "Original Title"  # Осталось прежним
    assert data["kind"] == "book"  # Осталось прежним

    # Обновляем только название
    r = client.put(f"/entries/{eid}", json={"title": "Updated Title"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == "completed"  # Осталось прежним


def test_get_stats(client):
    # Создаем несколько записей для статистики
    client.post("/entries", json={"title": "Book 1", "kind": "book", "status": "planned"})
    client.post("/entries", json={"title": "Article 1", "kind": "article", "status": "completed"})
    client.post("/entries", json={"title": "Course 1", "kind": "course", "status": "in_progress"})

    r = client.get("/entries/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["total_entries"] == 3
    assert "by_status" in data
    assert "by_kind" in data