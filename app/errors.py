# app/errors.py

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status


class ErrorCode(str, Enum):
    VALIDATION = "validation_error"
    NOT_FOUND = "not_found"
    FORBIDDEN = "forbidden"
    UNAUTHORIZED = "unauthorized"
    INTERNAL = "internal_error"
    HTTP = "http_error"


def _to_json_error(
    code: str,
    message: str,
    http_status: int,
    *,
    details: Iterable[dict[str, Any]] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = list(details)
    return JSONResponse(body, status_code=http_status, headers=headers or {})


def json_error(code: str, message: str, http_status: int) -> JSONResponse:
    return _to_json_error(code, message, http_status)


def not_found(message: str = "resource not found") -> JSONResponse:
    return _to_json_error(ErrorCode.NOT_FOUND, message, status.HTTP_404_NOT_FOUND)


def forbidden(message: str = "forbidden") -> JSONResponse:
    return _to_json_error(ErrorCode.FORBIDDEN, message, status.HTTP_403_FORBIDDEN)


def unauthorized(message: str = "unauthorized") -> JSONResponse:
    return _to_json_error(
        ErrorCode.UNAUTHORIZED,
        message,
        status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    def to_detail(err: dict[str, Any]) -> dict[str, Any]:
        loc = ".".join(str(x) for x in err.get("loc", []) if x != "body")
        return {"field": loc, "message": err.get("msg", "invalid value")}

    return _to_json_error(
        ErrorCode.VALIDATION,
        "invalid request",
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        details=[to_detail(e) for e in exc.errors() or []],
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    msg = exc.detail if isinstance(exc.detail, str) else "http error"
    return _to_json_error(ErrorCode.HTTP, msg, exc.status_code or 500)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return _to_json_error(
        ErrorCode.INTERNAL,
        "internal server error",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_error_handlers(app: FastAPI) -> None:
    """Подключить все хендлеры к приложению."""
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
