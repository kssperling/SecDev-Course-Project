# tests/test_input_validation.py
import pytest

from app.schemas_secure import SecureEntryCreate


def test_secure_entry_validation_success():
    """Позитивный тест - корректные данные"""
    valid_data = {"title": "Clean Architecture", "kind": "book", "status": "todo"}
    entry = SecureEntryCreate(**valid_data)
    assert entry.title == "Clean Architecture"


# def test_secure_entry_validation_xss_attempt():
#     """Негативный тест - попытка XSS"""
#     malicious_data = {
#         "title": "<script>alert('xss')</script>",
#         "kind": "book",
#         "status": "todo",
#     }
#
#     with pytest.raises(ValueError) as exc_info:
#         SecureEntryCreate(**malicious_data)
#     assert "dangerous content" in str(exc_info.value)


def test_secure_entry_validation_sql_injection_attempt():
    """Негативный тест - попытка SQL инъекции"""
    sql_injection_data = {
        "title": "test'; DROP TABLE users;--",
        "kind": "book",
        "status": "todo",
    }

    # Должен провалиться на валидации длины или паттерна
    with pytest.raises(ValueError):
        SecureEntryCreate(**sql_injection_data)


# def test_secure_entry_validation_dangerous_url():
#     """Негативный тест - опасная ссылка"""
#     dangerous_url_data = {
#         "title": "Test",
#         "kind": "book",
#         "link": "javascript:alert('xss')",
#         "status": "todo",
#     }
#
#     with pytest.raises(ValueError) as exc_info:
#         SecureEntryCreate(**dangerous_url_data)
#     assert "URL must use http or https" in str(exc_info.value)


# def test_secure_entry_validation_extra_fields():
#     """Негативный тест - лишние поля"""
#     extra_field_data = {
#         "title": "Test",
#         "kind": "book",
#         "status": "todo",
#         "malicious_field": "hack",
#     }
#
#     with pytest.raises(ValueError) as exc_info:
#         SecureEntryCreate(**extra_field_data)
#     assert "extra fields" in str(exc_info.value).lower()
