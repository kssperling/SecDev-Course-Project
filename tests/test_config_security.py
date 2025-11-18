# # tests/test_config_security.py
#
# import pytest
#
# from app.config_secure import SecureSettings, mask_secret_value, validate_config
#
#
# def test_secret_masking():
#     """Тест маскирования секретных значений"""
#     assert mask_secret_value("") == ""
#     assert mask_secret_value("ab") == "***"
#     assert mask_secret_value("abcd") == "***"
#     assert mask_secret_value("mysecretkey123") == "my***23"
#     assert mask_secret_value("verylongsecretkey") == "ve***ey"
#
#
# def test_config_validation():
#     """Тест валидации конфигурации"""
#     # Должен провалиться на коротком секретном ключе
#     with pytest.raises(ValueError) as exc_info:
#         invalid_settings = SecureSettings(secret_key="short", token_salt="somesalt")
#         validate_config(invalid_settings)
#     assert "at least 32 characters" in str(exc_info.value)
#
#
# def test_config_from_env(monkeypatch):
#     """Тест загрузки конфигурации из env переменных"""
#     monkeypatch.setenv("APP_SECRET_KEY", "test_secret_key_that_is_long_enough_123")
#     monkeypatch.setenv("TOKEN_SALT", "test_salt_123")
#
#     settings = SecureSettings()
#     assert settings.secret_key == "test_secret_key_that_is_long_enough_123"
#     assert settings.token_salt == "test_salt_123"
