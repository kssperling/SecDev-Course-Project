# app/resource_monitor.py
import logging
from datetime import datetime
from typing import Any, Dict

import psutil

resource_logger = logging.getLogger("resources")


class ResourceMonitor:
    def __init__(self):
        self._entry_limits = {
            "max_entries_per_user": 1000,
            "max_title_length": 255,
            "max_request_size": 1024 * 1024,  # 1MB
        }
        self._memory_threshold = 0.8  # 80% использования памяти

    def check_memory_usage(self) -> Dict[str, Any]:
        """Проверка использования памяти"""
        memory = psutil.virtual_memory()
        return {
            "total_mb": memory.total // (1024 * 1024),
            "used_mb": memory.used // (1024 * 1024),
            "percent_used": memory.percent,
            "is_critical": memory.percent > (self._memory_threshold * 100),
        }

    def check_entries_quota(self, username: str, current_entries: int) -> bool:
        """Проверка квоты записей пользователя"""
        if current_entries >= self._entry_limits["max_entries_per_user"]:
            resource_logger.warning(
                f"User {username} reached entries limit: {current_entries}/"
                f"{self._entry_limits['max_entries_per_user']}"
            )
            return False
        return True

    def validate_request_size(self, content_length: int) -> bool:
        """Проверка размера запроса"""
        if content_length > self._entry_limits["max_request_size"]:
            return False
        return True

    def get_system_health(self) -> Dict[str, Any]:
        """Полная проверка здоровья системы"""
        memory = self.check_memory_usage()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "memory": memory,
            "limits": self._entry_limits,
            "status": "healthy" if not memory["is_critical"] else "degraded",
        }


# Глобальный экземпляр монитора
resource_monitor = ResourceMonitor()
