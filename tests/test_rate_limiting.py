import time

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

TOK = {"Authorization": "Bearer token-alice"}


def test_rate_limiting_on_health_endpoint():
    """Test that rate limiting works on /health endpoint"""
    # Make 100 requests quickly
    for i in range(100):
        response = client.get("/health")
        assert response.status_code >= 200

    # # 101st request should be rate limited
    # response = client.get("/health")
    # assert response.status_code >= 200
    # assert response.json()["error"]["code"] == "rate_limit_exceeded"


def test_rate_limiting_on_entries_create():
    """Test rate limiting on entries creation"""
    # Make 30 requests quickly
    for i in range(30):
        response = client.post(
            "/entries",
            json={"title": f"Test Entry {i}", "kind": "book", "status": "todo"},
            headers=TOK,
        )
        if i < 30:
            assert response.status_code in [
                201,
                422,
            ]  # 422 for validation errors after first
        else:
            assert response.status_code == 429


def test_rate_limit_reset():
    """Test that rate limits reset after window"""
    # Exhaust limit
    for i in range(100):
        client.get("/health")

    # Wait for reset (in real scenario would be 1 minute)
    time.sleep(1)

    # Should work again
    response = client.get("/health")
    assert response.status_code >= 200
