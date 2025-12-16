# app/errors_secure_fixed.py
import logging
from uuid import uuid4

from fastapi import Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("security")


def create_problem_response(
    status: int,
    title: str,
    detail: str,
    error_type: str = "about:blank",
    instance: str = "",
) -> JSONResponse:
    """Создание ответа в формате RFC 7807"""
    correlation_id = str(uuid4())

    problem_data = {
        "type": error_type,
        "title": title,
        "status": status,
        "detail": detail,
        "correlation_id": correlation_id,
        "instance": instance,
    }

    logger.info(f"Error {status}: {title} - Correlation: {correlation_id}")

    return JSONResponse(
        status_code=status,
        content=problem_data,
        headers={
            "Content-Type": "application/problem+json",
            "X-Correlation-ID": correlation_id,
        },
    )


async def secure_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    """Обработчик ошибок валидации"""
    return create_problem_response(
        status=422,
        title="Validation Failed",
        detail="The request contains invalid parameters",
        error_type="https://api.example.com/errors/validation-failed",
        instance=str(request.url),
    )


async def secure_http_exception_handler(request: Request, exc: HTTPException):
    """Обработчик HTTP исключений"""
    # Маппинг статус кодов
    status_mapping = {
        400: ("Bad Request", "The request is invalid"),
        401: ("Unauthorized", "Authentication required"),
        403: ("Forbidden", "Access to the resource is forbidden"),
        404: ("Not Found", "The requested resource was not found"),
        405: ("Method Not Allowed", "HTTP method not allowed"),
        409: ("Conflict", "Resource conflict"),
        500: ("Internal Server Error", "An internal server error occurred"),
        503: ("Service Unavailable", "Service temporarily unavailable"),
    }

    title, default_detail = status_mapping.get(
        exc.status_code, ("HTTP Error", "An error occurred")
    )

    # Используем детали из исключения или дефолтные
    detail = (
        exc.detail
        if (hasattr(exc, "detail") and isinstance(exc.detail, str))
        else default_detail
    )

    return create_problem_response(
        status=exc.status_code,
        title=title,
        detail=detail,
        error_type=f"https://api.example.com/errors/http-{exc.status_code}",
        instance=str(request.url),
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Обработчик всех необработанных исключений"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return create_problem_response(
        status=500,
        title="Internal Server Error",
        detail="An unexpected error occurred",
        error_type="https://api.example.com/errors/internal-error",
        instance=str(request.url),
    )
