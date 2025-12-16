# app/token_security.py
import hashlib
import secrets
from datetime import datetime
from typing import Dict, Optional


class TokenManager:
    def __init__(self):
        self._token_map: Dict[str, Dict] = {}
        self._initialize_default_tokens()

    def _initialize_default_tokens(self):
        """Инициализация тестовых токенов с хэшированием"""
        test_tokens = {"alice": "token-alice", "bob": "token-bob"}

        for username, token in test_tokens.items():
            hashed_token = self._hash_token(token)
            self._token_map[hashed_token] = {
                "username": username,
                "created_at": datetime.utcnow(),
                "last_used": None,
            }

    def _hash_token(self, token: str) -> str:
        """Хэширование токена с солью"""
        salt = "secure_salt_2024"  # В продакшене брать из env переменных
        return hashlib.sha256(f"{token}{salt}".encode()).hexdigest()

    def validate_token(self, token: str) -> Optional[str]:
        """Валидация токена и возврат username"""
        hashed_token = self._hash_token(token.strip())
        token_data = self._token_map.get(hashed_token)

        if token_data:
            # Обновляем время последнего использования
            token_data["last_used"] = datetime.utcnow()
            return token_data["username"]

        return None

    def create_token(self, username: str) -> str:
        """Создание нового безопасного токена"""
        # Генерируем криптографически безопасный токен
        raw_token = secrets.token_urlsafe(32)
        hashed_token = self._hash_token(raw_token)

        self._token_map[hashed_token] = {
            "username": username,
            "created_at": datetime.utcnow(),
            "last_used": None,
        }

        return raw_token

    def revoke_token(self, token: str) -> bool:
        """Отзыв токена"""
        hashed_token = self._hash_token(token)
        if hashed_token in self._token_map:
            del self._token_map[hashed_token]
            return True
        return False

    def get_token_stats(self) -> Dict:
        """Статистика токенов (для админки)"""
        return {
            "total_tokens": len(self._token_map),
            "active_users": list(
                set(data["username"] for data in self._token_map.values())
            ),
        }


# Глобальный экземпляр менеджера токенов
token_manager = TokenManager()
