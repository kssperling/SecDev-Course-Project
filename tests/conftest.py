import os
import sys

import pytest
from fastapi.testclient import TestClient

from app.main import _ENTRIES_DB, app  # Теперь импортируем из корня

# Добавляем корневую директорию в путь Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(autouse=True)
def reset_state():
    """Очищаем in-memory хранилище перед/после каждого теста."""
    _ENTRIES_DB.clear()
    yield
    _ENTRIES_DB.clear()


@pytest.fixture()
def client():
    """HTTP-клиент FastAPI для интеграционных тестов."""
    with TestClient(app) as c:
        yield c
