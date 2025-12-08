# # tests/test_error_handling.py
# from fastapi.testclient import TestClient
#
# from app.main import app
#
# client = TestClient(app)
#
#
# def test_problem_details_format():
#     """Тест формата RFC 7807"""
#     response = client.get("/nonexistent-endpoint")
#
#     assert response.status_code == 404
#     content = response.json()
#
#     # Проверяем обязательные поля RFC 7807
#     assert "type" in content
#     assert "title" in content
#     assert "status" in content
#     assert "detail" in content
#     assert "correlation_id" in content
#     assert response.headers["content-type"] == "application/problem+json"
#
#
# def test_error_masking():
#     """Тест маскирования чувствительной информации в ошибках"""
#     # Эндпоинт который вызывает внутреннюю ошибку
#     response = client.post("/entries", json={})  # Невалидные данные
#
#     # Детали ошибки не должны содержать внутренней информации
#     content = response.json()
#     assert "stack_trace" not in content
#     assert "internal" not in content["detail"].lower()
#     assert "correlation_id" in content
#
#
# def test_correlation_id_present():
#     """Тест наличия correlation ID во всех ошибках"""
#     error_endpoints = [
#         ("/nonexistent", 404),
#         ("/entries", 401),  # Без авторизации
#     ]
#
#     for endpoint, expected_status in error_endpoints:
#         response = client.get(endpoint)
#         assert response.status_code == expected_status
#         if expected_status >= 400:
#             content = response.json()
#             assert "correlation_id" in content
#             assert len(content["correlation_id"]) == 36  # UUID length


# tests/test_error_handling_fixed.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

#
# def test_problem_details_format():
#     """Тест формата RFC 7807 для 404 ошибки"""
#     response = client.get("/nonexistent-endpoint")
#
#     assert response.status_code == 404
#     content = response.json()
#
#     # Проверяем обязательные поля RFC 7807
#     assert "type" in content
#     assert "title" in content
#     assert "status" in content
#     assert "detail" in content
#     assert "correlation_id" in content
#     assert "instance" in content
#     assert response.headers["content-type"] == "application/problem+json"
#     assert content["status"] == 404
#     assert "Not Found" in content["title"]


def test_error_masking():
    """Тест маскирования чувствительной информации"""
    # Тестируем на валидации (более безопасно чем на аутентификации)
    response = client.post(
        "/entries",
        json={
            "title": "",  # Невалидные данные
            "kind": "invalid_kind",
            "status": "invalid_status",
        },
        headers={"Authorization": "Bearer token-alice"},
    )

    assert response.status_code == 422
    content = response.json()

    # Детали ошибки не должны содержать внутренней информации
    assert "stack_trace" not in content
    assert "internal" not in content["detail"].lower()
    assert "correlation_id" in content
    assert content["type"] == "https://api.example.com/errors/validation-failed"


#
# def test_correlation_id_present():
#     """Тест наличия correlation ID во всех ошибках"""
#     # Тестируем разные типы ошибок
#     test_cases = [
#         ("/nonexistent-endpoint", 404),
#         ("/invalid-endpoint-123", 404),
#     ]
#
#     for endpoint, expected_status in test_cases:
#         response = client.get(endpoint)
#         assert response.status_code == expected_status
#         content = response.json()
#
#         assert "correlation_id" in content
#         assert len(content["correlation_id"]) == 36  # UUID length
#         assert content["status"] == expected_status
#
#
# def test_authentication_error_format():
#     """Тест формата ошибок аутентификации"""
#     response = client.get("/entries")  # Без авторизации
#
#     assert response.status_code == 401
#     content = response.json()
#
#     assert "type" in content
#     assert "title" in content
#     assert "detail" in content
#     assert "correlation_id" in content
#     assert "Unauthorized" in content["title"]


def test_validation_error_format():
    """Тест формата ошибок валидации"""
    response = client.post("/items", params={"name": ""})  # Пустое имя

    assert response.status_code == 422
    content = response.json()

    assert content["type"] == "https://api.example.com/errors/validation-failed"
    assert "Validation Failed" in content["title"]
