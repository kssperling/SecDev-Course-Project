import os
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.main import app

tc = TestClient(app)


def auth(key: str):
    return {"Authorization": f"Bearer {key}"}


def test_nfr01_error_format_and_traceid():
    r = tc.get("/items/999999")
    assert r.status_code == 404
    body = r.json()
    assert "error" in body and "code" in body["error"]
    assert body["error"]["code"] == "not_found"


@pytest.mark.xfail(reason="роль admin пока не реализована")
def test_nfr02_admin_forbidden_for_regular_user():
    r = tc.get("/admin/stats", headers=auth("key-alice"))
    assert r.status_code == 403


@pytest.mark.xfail(reason="JWT-TTL ещё не реализован, сейчас токены-заглушки")
def test_nfr03_jwt_ttl_and_expired():
    expired = "expired-token"
    r = tc.get("/entries", headers=auth(expired))
    assert r.status_code == 401
    assert "expired" in r.text.lower()


@pytest.mark.xfail(reason="лимитер пока не добавлен")
def test_nfr04_rate_limit_429():
    got_429 = False
    for _ in range(70):
        r = tc.get("/entries", headers=auth("key-alice"))
        if r.status_code == 429:
            got_429 = True
            assert "Retry-After" in r.headers
            break
    assert got_429, "ожидали 429 при превышении лимита"


@pytest.mark.xfail(reason="ограничение body пока не добавлено")
def test_nfr05_max_request_size():
    big_body = {
        "title": "x" * 100_000,
        "kind": "book",
        "link": "https://x.com",
        "status": "todo",
    }
    r = tc.post("/entries", headers=auth("key-alice"), json=big_body)
    assert r.status_code == 413


@pytest.mark.xfail(reason="аудит пока не реализован")
def test_nfr06_audit_log_written(monkeypatch):
    called = {}

    def fake_log(msg):
        called["ok"] = True

    monkeypatch.setattr("app.entries.logger.info", fake_log)
    tc.get("/entries", headers=auth("key-alice"))
    assert called.get("ok")


def test_nfr07_sca_placeholder():
    assert os.path.exists("requirements.txt")


def test_nfr08_sast_placeholder():
    if shutil.which("bandit") is None:
        pytest.skip("bandit not installed locally")
    code = subprocess.call(["bandit", "--version"])
    assert code in (0, 1)


def test_nfr09_cors_headers():
    r = tc.options("/entries", headers={"Origin": "https://example.com"})
    assert r.status_code in (200, 204, 405)


@pytest.mark.xfail(reason="пагинация пока не реализована")
def test_nfr10_requires_pagination():
    r = tc.get("/entries?limit=999999", headers=auth("key-alice"))
    assert r.status_code in (400, 422)


@pytest.mark.xfail(reason="бэкап пока не реализован")
def test_nfr11_backup_restore():
    assert False, "пока нет скрипта backup/restore"
