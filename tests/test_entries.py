# tests/test_entries.py
TOK = {"Authorization": "Bearer token-alice"}


def test_crud_flow(client):
    r = client.post(
        "/entries",
        json={
            "title": "Clean Architecture",
            "kind": "book",
            "link": None,
            "status": "todo",
        },
        headers=TOK,
    )
    assert r.status_code == 201, r.text
    eid = r.json()["id"]

    r = client.get(f"/entries/{eid}", headers=TOK)
    assert r.status_code == 200
    assert r.json()["title"] == "Clean Architecture"

    r = client.get("/entries", headers=TOK)
    assert r.status_code == 200
    assert any(x["id"] == eid for x in r.json())

    r = client.get("/entries?status=todo", headers=TOK)
    assert r.status_code == 200
    assert all(x["status"] == "todo" for x in r.json())

    r = client.patch(f"/entries/{eid}", json={"status": "reading"}, headers=TOK)
    assert r.status_code == 200
    assert r.json()["status"] == "reading"

    r = client.delete(f"/entries/{eid}", headers=TOK)
    assert r.status_code == 204


def test_owner_isolated(client):
    r = client.post(
        "/entries",
        json={"title": "Paper A", "kind": "paper", "status": "todo"},
        headers={"Authorization": "Bearer token-alice"},
    )
    eid = r.json()["id"]
    r = client.get(f"/entries/{eid}", headers={"Authorization": "Bearer token-bob"})
    assert r.status_code in (403, 404)
    r = client.delete(f"/entries/{eid}", headers={"Authorization": "Bearer token-bob"})
    assert r.status_code in (403, 404)


def test_validation(client):
    r = client.post(
        "/entries", json={"title": "", "kind": "book", "status": "todo"}, headers=TOK
    )
    assert r.status_code == 422
    r = client.get("/entries?status=weird", headers=TOK)
    assert r.status_code == 422


def test_auth_required(client):
    r = client.get("/entries")
    assert r.status_code == 401
