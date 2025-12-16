from __future__ import annotations

from datetime import datetime
from typing import Dict

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.auth import get_current_user
from app.entries import _ENTRIES_DB, EntryStatus, _next_id, _user_store
from app.entries import router as entries_router
from app.errors import register_error_handlers
from app.errors_secure import secure_http_exception_handler, secure_validation_exception_handler
from app.errors_secure_fixed import generic_exception_handler
from app.security import limiter, rate_limit_exceeded_handler

# В начало файла добавьте
from app.security_headers import add_security_middlewares

from .entries import EntryCreate
from .resource_monitor import resource_monitor

# После создания app добавьте
app = FastAPI(title="SecDev Course App", version="0.1.0")
add_security_middlewares(app)  # Добавить эту строку

# Регистрируем обработчики ПЕРВЫМИ
app.add_exception_handler(RequestValidationError, secure_validation_exception_handler)
app.add_exception_handler(HTTPException, secure_http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Остальной код...
register_error_handlers(
    app
)  # Если эта функция регистрирует старые обработчики - УДАЛИТЕ её

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.include_router(entries_router)
__all__ = ["app", "_ENTRIES_DB"]

app = FastAPI(title="SecDev Course App", version="0.1.0")


# Регистрируем обработчики ПЕРВЫМИ
app.add_exception_handler(RequestValidationError, secure_validation_exception_handler)
app.add_exception_handler(HTTPException, secure_http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Остальной код...
register_error_handlers(
    app
)  # Если эта функция регистрирует старые обработчики - УДАЛИТЕ её

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.include_router(entries_router)


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400):
        self.code = code
        self.message = message
        self.status = status


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    headers = {"WWW-Authenticate": "Bearer"} if exc.code == "unauthorized" else {}
    return JSONResponse(
        status_code=exc.status,
        content={"error": {"code": exc.code, "message": exc.message}},
        headers=headers,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={"error": {"code": "not_found", "message": "Not Found"}},
        )
    detail = exc.detail if isinstance(exc.detail, str) else "http_error"
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": detail}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    raw = exc.errors()
    safe_details = []
    for err in raw:
        e = dict(err)
        ctx = e.get("ctx")
        if isinstance(ctx, dict):
            e["ctx"] = {
                k: (str(v) if isinstance(v, BaseException) else v)
                for k, v in ctx.items()
            }
        safe_details.append(e)

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Validation error",
                "details": safe_details,
            }
        },
    )


_ITEMS_DB: Dict[int, Dict] = {}

_DB = {"items": []}


@app.post("/items")
def create_item(name: str = Query(min_length=1)):
    new_id = (max(_ITEMS_DB) + 1) if _ITEMS_DB else 1
    _ITEMS_DB[new_id] = {"id": new_id, "name": name}
    return _ITEMS_DB[new_id]


@app.get("/items/{item_id}")
def get_item(item_id: int):
    item = _ITEMS_DB.get(item_id)
    if not item:
        raise HTTPException(status_code=404)
    return item


@app.get("/health", tags=["system"], summary="Health check")
@limiter.limit("100/minute")
def health(request: Request):
    return {"status": "ok"}


# @app.get("/entries", response_model=list[EntryOut], summary="List entries")
# @limiter.limit("60/minute")
def list_entries(
    request: Request,
    username: str = Depends(get_current_user),
    status_: EntryStatus | None = Query(default=None, alias="status"),
):
    us = _user_store(username)
    items = us["entries"]
    if status_:
        items = [e for e in items if e["status"] == status_]
    return list(sorted(items, key=lambda e: e["id"], reverse=True))


# @app.post("/entries", response_model=EntryOut, status_code=201, summary="Create entry")
# @limiter.limit("30/minute")
def create_entry(
    request: Request,
    payload: EntryCreate,
    username: str = Depends(get_current_user),
):
    us = _user_store(username)
    entry = {
        "id": _next_id(us),
        "title": payload.title,
        "kind": payload.kind,
        "link": str(payload.link) if payload.link is not None else None,
        "status": payload.status,
    }
    us["entries"].append(entry)
    return entry


@app.get("/system/health", tags=["system"])
def system_health():
    """Расширенная проверка здоровья системы"""
    health_data = resource_monitor.get_system_health()

    if health_data["status"] == "degraded":
        return JSONResponse(
            status_code=503, content={"status": "degraded", "details": health_data}
        )

    return {"status": "healthy", "details": health_data}


@app.get("/system/metrics", tags=["system"])
def system_metrics():
    """Метрики системы для мониторинга"""
    return resource_monitor.get_system_health()


# Заменяем обработчики ошибок
app.add_exception_handler(RequestValidationError, secure_validation_exception_handler)
app.add_exception_handler(HTTPException, secure_http_exception_handler)


# В app/main.py добавьте или обновите эндпоинты:


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/v1/info")
def api_info():
    """API information endpoint"""
    return {
        "name": "SecDev Course API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": ["/health", "/entries", "/items", "/system/health"],
    }


@app.post("/api/v1/echo")
async def echo_endpoint(data: dict):
    """Echo endpoint for testing POST requests"""
    return {"received": data, "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/v1/users/{user_id}")
def get_user(user_id: int):
    """User endpoint for testing path parameters"""
    return {"user_id": user_id, "username": f"user_{user_id}"}


@app.get("/api/v1/search")
def search_items(q: str = Query(None), limit: int = Query(10)):
    """Search endpoint for testing query parameters"""
    return {"query": q, "limit": limit, "results": []}
