# app/audit.py
import logging
from datetime import datetime
from typing import Any, Dict

# Настройка логгера для аудита
audit_logger = logging.getLogger("audit")
audit_logger.setLevel(logging.INFO)

# Создаем handler для записи в файл
handler = logging.FileHandler("audit.log")
handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
audit_logger.addHandler(handler)


class AuditOperation:
    CREATE = "create_entry"
    READ = "read_entry"
    UPDATE = "update_entry"
    DELETE = "delete_entry"
    LIST = "list_entries"


def log_audit_event(
    username: str, operation: str, entry_id: int = None, details: Dict[str, Any] = None
):
    """Логирование событий аудита в структурированном формате"""
    audit_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": username,
        "operation": operation,
        "entry_id": entry_id,
        "details": details or {},
    }

    audit_logger.info(f"AUDIT: {audit_data}")
