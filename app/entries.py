# app/entries.py

from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, Depends, Query, Response
from pydantic import AnyHttpUrl, BaseModel, field_validator

from app.audit import AuditOperation, log_audit_event
from app.auth import ApiError, get_current_user
from app.resource_monitor import resource_monitor

router = APIRouter(prefix="/entries", tags=["entries"])

EntryKind = Literal["book", "article", "paper", "video"]
EntryStatus = Literal["todo", "reading", "done", "archived"]


class EntryCreate(BaseModel):
    title: str
    kind: EntryKind
    link: Optional[AnyHttpUrl] = None
    status: EntryStatus = "todo"

    @field_validator("title")
    @classmethod
    def _title_not_blank(cls, v: str):
        v = v.strip()
        if not v:
            raise ValueError("title cannot be empty")
        if len(v) > 255:
            raise ValueError("title too long")
        return v


class EntryUpdate(BaseModel):
    title: Optional[str] = None
    kind: Optional[EntryKind] = None
    link: Optional[AnyHttpUrl] = None
    status: Optional[EntryStatus] = None

    @field_validator("title")
    @classmethod
    def _title_not_blank(cls, v: Optional[str]):
        if v is None:
            return v
        v2 = v.strip()
        if not v2:
            raise ValueError("title cannot be empty")
        if len(v2) > 255:
            raise ValueError("title too long")
        return v2


class EntryOut(BaseModel):
    id: int
    title: str
    kind: EntryKind
    link: Optional[str] = None
    status: EntryStatus


_ENTRIES_DB: Dict[str, Dict[str, Any]] = {}


def _user_store(username: str) -> Dict[str, Any]:
    if username not in _ENTRIES_DB:
        _ENTRIES_DB[username] = {"seq": 0, "entries": []}
    return _ENTRIES_DB[username]


def _next_id(us: Dict[str, Any]) -> int:
    us["seq"] += 1
    return us["seq"]


def _find_entry(us: Dict[str, Any], entry_id: int) -> Optional[Dict[str, Any]]:
    for e in us["entries"]:
        if e["id"] == entry_id:
            return e
    return None


# @router.post("", response_model=EntryOut, status_code=201, summary="Create entry")
# def create_entry(payload: EntryCreate, username: str = Depends(get_current_user)):
#     us = _user_store(username)
#     entry = {
#         "id": _next_id(us),
#         "title": payload.title,
#         "kind": payload.kind,
#         "link": str(payload.link) if payload.link is not None else None,
#         "status": payload.status,
#     }
#     us["entries"].append(entry)
#     return entry


@router.get("", response_model=list[EntryOut], summary="List entries (with ?status=)")
def list_entries(
    username: str = Depends(get_current_user),
    status_: Optional[EntryStatus] = Query(default=None, alias="status"),
):
    us = _user_store(username)
    items = us["entries"]
    if status_:
        items = [e for e in items if e["status"] == status_]
    return list(sorted(items, key=lambda e: e["id"], reverse=True))


# @router.get("/{entry_id}", response_model=EntryOut, summary="Get entry by id")
# def get_entry(entry_id: int, username: str = Depends(get_current_user)):
#     us = _user_store(username)
#     entry = _find_entry(us, entry_id)
#     if not entry:
#         raise ApiError("not_found", "entry not found", 404)
#     return entry
#
#
# @router.patch("/{entry_id}", response_model=EntryOut, summary="Patch entry")
# def patch_entry(
#     entry_id: int, payload: EntryUpdate, username: str = Depends(get_current_user)
# ):
#     us = _user_store(username)
#     entry = _find_entry(us, entry_id)
#     if not entry:
#         raise ApiError("not_found", "entry not found", 404)
#
#     if payload.title is not None:
#         entry["title"] = payload.title
#     if payload.kind is not None:
#         entry["kind"] = payload.kind
#     if payload.link is not None:
#         entry["link"] = str(payload.link)
#     if payload.status is not None:
#         entry["status"] = payload.status
#     return entry


# @router.delete("/{entry_id}", status_code=204, summary="Delete entry")
# def delete_entry(entry_id: int, username: str = Depends(get_current_user)):
#     us = _user_store(username)
#     entry = _find_entry(us, entry_id)
#     if not entry:
#         raise ApiError("not_found", "entry not found", 404)
#     us["entries"] = [e for e in us["entries"] if e["id"] != entry_id]
#     return Response(status_code=204)
#
#
# __all__ = ["router", "_ENTRIES_DB"]

# app/entries.py (дополнение)


# @router.post("", response_model=EntryOut, status_code=201)
# def create_entry(payload: EntryCreate, username: str = Depends(get_current_user)):
#     us = _user_store(username)
#     entry_id = _next_id(us)
#     entry = {
#         "id": entry_id,
#         "title": payload.title,
#         "kind": payload.kind,
#         "link": str(payload.link) if payload.link is not None else None,
#         "status": payload.status,
#     }
#     us["entries"].append(entry)
#
#     # Аудит создания записи
#     log_audit_event(
#         username=username,
#         operation=AuditOperation.CREATE,
#         entry_id=entry_id,
#         details={"title": payload.title, "kind": payload.kind}
#     )
#
#     return entry


@router.get("/{entry_id}", response_model=EntryOut)
def get_entry(entry_id: int, username: str = Depends(get_current_user)):
    us = _user_store(username)
    entry = _find_entry(us, entry_id)
    if not entry:
        raise ApiError("not_found", "entry not found", 404)

    # Аудит чтения записи
    log_audit_event(username=username, operation=AuditOperation.READ, entry_id=entry_id)

    return entry


@router.patch("/{entry_id}", response_model=EntryOut)
def patch_entry(
    entry_id: int, payload: EntryUpdate, username: str = Depends(get_current_user)
):
    us = _user_store(username)
    entry = _find_entry(us, entry_id)
    if not entry:
        raise ApiError("not_found", "entry not found", 404)

    # Логируем изменения перед применением
    changes = {}
    if payload.title is not None and payload.title != entry["title"]:
        changes["title"] = {"old": entry["title"], "new": payload.title}
    if payload.status is not None and payload.status != entry["status"]:
        changes["status"] = {"old": entry["status"], "new": payload.status}

    # Применяем изменения
    if payload.title is not None:
        entry["title"] = payload.title
    if payload.kind is not None:
        entry["kind"] = payload.kind
    if payload.link is not None:
        entry["link"] = str(payload.link)
    if payload.status is not None:
        entry["status"] = payload.status

    # Аудит обновления
    log_audit_event(
        username=username,
        operation=AuditOperation.UPDATE,
        entry_id=entry_id,
        details={"changes": changes},
    )

    return entry


@router.delete("/{entry_id}", status_code=204)
def delete_entry(entry_id: int, username: str = Depends(get_current_user)):
    us = _user_store(username)
    entry = _find_entry(us, entry_id)
    if not entry:
        raise ApiError("not_found", "entry not found", 404)

    # Аудит удаления
    log_audit_event(
        username=username,
        operation=AuditOperation.DELETE,
        entry_id=entry_id,
        details={"title": entry["title"]},
    )

    us["entries"] = [e for e in us["entries"] if e["id"] != entry_id]
    return Response(status_code=204)


# app/entries.py (дополнения)


@router.post("", response_model=EntryOut, status_code=201)
def create_entry(payload: EntryCreate, username: str = Depends(get_current_user)):
    us = _user_store(username)

    # Проверка квоты записей
    current_count = len(us["entries"])
    if not resource_monitor.check_entries_quota(username, current_count):
        raise ApiError(
            "quota_exceeded",
            f"Maximum entries limit reached ({current_count}/1000)",
            429,
        )

    # Проверка использования памяти
    # memory_status = resource_monitor.check_memory_usage()
    # if memory_status["is_critical"]:
    #     raise ApiError(
    #         "system_overload", "System is under heavy load, please try again later", 503
    #     )

    entry_id = _next_id(us)
    entry = {
        "id": entry_id,
        "title": payload.title,
        "kind": payload.kind,
        "link": str(payload.link) if payload.link is not None else None,
        "status": payload.status,
    }
    us["entries"].append(entry)

    log_audit_event(username, AuditOperation.CREATE, entry_id)
    return entry
