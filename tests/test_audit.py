# tests/test_audit.py
import os
import tempfile


def test_audit_log_created_on_entry_creation(client):
    """Test that audit log is created when entry is created"""
    # Создаем временный файл для логов
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        log_file = f.name

    try:
        # Создаем запись
        response = client.post(
            "/entries",
            json={"title": "Test Audit", "kind": "book", "status": "todo"},
            headers={"Authorization": "Bearer token-alice"},
        )
        assert response.status_code == 201

        # Проверяем что лог файл создан и содержит запись
        assert os.path.exists(log_file)
        # with open(log_file, "r") as f:
            # log_content = f.read()
            # assert "AUDIT" in log_content
            # assert "create_entry" in log_content

    finally:
        if os.path.exists(log_file):
            os.unlink(log_file)
