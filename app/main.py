# app/main.py
from __future__ import annotations

from typing import Dict

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.entries import _ENTRIES_DB
from app.entries import router as entries_router
from app.errors import register_error_handlers

app = FastAPI(title="SecDev Course App", version="0.1.0")
register_error_handlers(app)


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


# @app.get("/health")
# def health():
#     return {"status": "ok"}


# Example minimal entity (for tests/demo)
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
def health():
    return {"status": "ok"}


app.include_router(entries_router)
__all__ = ["app", "_ENTRIES_DB"]
