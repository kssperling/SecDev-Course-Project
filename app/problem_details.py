# app/problem_details.py
import logging
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi.responses import JSONResponse


class ProblemDetails:
    def __init__(self):
        self.logger = logging.getLogger("security")

    def create_problem_response(
        self,
        status: int,
        title: str,
        detail: str,
        error_type: str = "about:blank",
        instance: Optional[str] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> JSONResponse:
        """Создание ответа в формате RFC 7807"""
        correlation_id = str(uuid4())

        problem_data = {
            "type": error_type,
            "title": title,
            "status": status,
            "detail": detail,
            "correlation_id": correlation_id,
            "instance": instance or "",
        }

        # Безопасное логирование (без чувствительных данных)
        self.logger.warning(
            f"Problem occurred: type={error_type}, title={title}, "
            f"status={status}, correlation_id={correlation_id}"
        )

        if extra_fields:
            problem_data.update(extra_fields)

        return JSONResponse(
            status_code=status,
            content=problem_data,
            headers={
                "Content-Type": "application/problem+json",
                "X-Correlation-ID": correlation_id,
            },
        )


# Глобальный экземпляр
problem_details = ProblemDetails()


# Декоратор для обработки ошибок
def safe_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Маскирование потенциально чувствительной информации
            safe_detail = "An error occurred while processing your request"

            # Логируем полную ошибку для дебага (в продакшене только безопасная информация)
            logging.error(f"Unhandled exception: {str(e)}", exc_info=True)

            return problem_details.create_problem_response(
                status=500,
                title="Internal Server Error",
                detail=safe_detail,
                error_type="https://api.example.com/errors/internal-error",
            )

    return wrapper


def secure_error_handler():
    return None
