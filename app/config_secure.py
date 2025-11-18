# app/config_secure.py
import logging
import os
from typing import Optional

from pydantic import BaseSettings, Field


class SecureSettings(BaseSettings):
    """Безопасная конфигурация приложения"""

    # Секретные значения только через env переменные
    secret_key: str = Field(..., env="APP_SECRET_KEY")
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    token_salt: str = Field(..., env="TOKEN_SALT")

    # Настройки безопасности
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # CORS настройки
    allowed_origins: list = Field(["http://localhost:3000"], env="ALLOWED_ORIGINS")

    class Config:
        env_file = ".env"
        case_sensitive = True


def validate_config(settings: SecureSettings) -> None:
    """Валидация конфигурации безопасности"""
    errors = []

    if settings.debug and "production" in os.environ.get("ENVIRONMENT", ""):
        errors.append("Debug mode should not be enabled in production")

    if len(settings.secret_key) < 32:
        errors.append("Secret key must be at least 32 characters long")

    if any(secret in str(settings.database_url) for secret in ["password", "secret"]):
        errors.append("Potential secret leak in database URL")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")


def mask_secret_value(value: str) -> str:
    """Маскирование секретных значений для логов"""
    if not value:
        return ""
    if len(value) <= 8:
        return "***"
    return value[:2] + "***" + value[-2:]


# Безопасный логгер для конфигов
secure_logger = logging.getLogger("secure_config")


def log_config_safely(settings: SecureSettings):
    """Безопасное логирование конфигурации"""
    secure_logger.info("Application configuration loaded")
    secure_logger.info(f"Debug mode: {settings.debug}")
    secure_logger.info(f"Log level: {settings.log_level}")
    secure_logger.info(f"Secret key: {mask_secret_value(settings.secret_key)}")
    secure_logger.info(f"Token salt: {mask_secret_value(settings.token_salt)}")

    if settings.database_url:
        # Маскируем пароль в database URL
        masked_url = settings.database_url
        if "://" in masked_url and "@" in masked_url:
            # Маскируем credentials в URL
            parts = masked_url.split("@", 1)
            masked_url = "://***:***@".join(parts)
        secure_logger.info(f"Database URL: {masked_url}")
