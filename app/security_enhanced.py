# app/security_enhanced.py
import logging
import time
from typing import Dict, Tuple

from slowapi import Limiter
from slowapi.util import get_remote_address


class EnhancedLimiter:
    def __init__(self):
        self.limiter = Limiter(key_func=get_remote_address)
        self.failed_attempts: Dict[str, Tuple[int, float]] = {}
        self.max_failed_attempts = 5
        self.lockout_duration = 900  # 15 минут

    def get_key_with_enhanced_security(self, request) -> str:
        """Улучшенный ключ для rate limiting с учетом пути"""
        client_ip = get_remote_address(request)
        path = request.url.path
        return f"{client_ip}:{path}"

    def record_failed_attempt(self, client_ip: str) -> bool:
        """Запись неудачной попытки и проверка блокировки"""
        now = time.time()

        if client_ip in self.failed_attempts:
            count, first_attempt = self.failed_attempts[client_ip]

            # Сброс счетчика если прошло больше lockout_duration
            if now - first_attempt > self.lockout_duration:
                self.failed_attempts[client_ip] = (1, now)
                return False

            # Увеличиваем счетчик
            self.failed_attempts[client_ip] = (count + 1, first_attempt)

            # Проверяем блокировку
            if count + 1 >= self.max_failed_attempts:
                logging.warning(f"IP {client_ip} temporarily locked out due to failed attempts")
                return True
        else:
            # Первая неудачная попытка
            self.failed_attempts[client_ip] = (1, now)

        return False

    def reset_failed_attempts(self, client_ip: str):
        """Сброс счетчика неудачных попыток"""
        if client_ip in self.failed_attempts:
            del self.failed_attempts[client_ip]

    def is_ip_locked(self, client_ip: str) -> bool:
        """Проверка блокировки IP"""
        if client_ip not in self.failed_attempts:
            return False

        count, first_attempt = self.failed_attempts[client_ip]
        if count >= self.max_failed_attempts:
            # Проверяем не истекла ли блокировка
            if time.time() - first_attempt < self.lockout_duration:
                return True
            else:
                # Сбрасываем если блокировка истекла
                del self.failed_attempts[client_ip]

        return False


# Глобальный экземпляр
enhanced_limiter = EnhancedLimiter()
