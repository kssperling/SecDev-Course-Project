# tests/test_errors.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_not_found_item():
    r = client.get("/items/999")
    assert r.status_code == 404
    body = r.json()
    # Новый формат RFC 7807
    assert "title" in body
    assert "detail" in body
    assert "status" in body
    assert "correlation_id" in body
    assert body["status"] == 404
    assert "not found" in body["detail"].lower()


def test_validation_error():
    r = client.post("/items", params={"name": ""})
    assert r.status_code == 422
    body = r.json()
    # Новый формат RFC 7807
    assert "title" in body
    assert "detail" in body
    assert "status" in body
    assert "correlation_id" in body
    assert body["status"] == 422
    assert "validation" in body["title"].lower()
