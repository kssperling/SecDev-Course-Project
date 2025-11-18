# app/token_security_secure.py
import hashlib

from app.config_secure import SecureSettings

settings = SecureSettings()


class SecureTokenManager:
    def __init__(self):
        self.salt = settings.token_salt

    def _hash_token(self, token: str) -> str:
        """Безопасное хэширование токена с солью из конфига"""
        return hashlib.sha256(f"{token}{self.salt}".encode()).hexdigest()

    def validate_token(self, token: str) -> bool:
        """Валидация токена без утечек во времени"""
        # Постоянное время выполнения для предотвращения timing attacks
        expected_hash = self._hash_token("expected_token")
        actual_hash = self._hash_token(token)

        # Сравнение с постоянным временем выполнения
        if len(expected_hash) != len(actual_hash):
            return False

        result = 0
        for x, y in zip(expected_hash, actual_hash):
            result |= ord(x) ^ ord(y)
        return result == 0
