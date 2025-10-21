# app/entries.py

from __future__ import annotations

from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, Depends, Query, Response
from pydantic import AnyHttpUrl, BaseModel, field_validator

from app.auth import ApiError, get_current_user

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


@router.post("", response_model=EntryOut, status_code=201, summary="Create entry")
def create_entry(payload: EntryCreate, username: str = Depends(get_current_user)):
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


@router.get("/{entry_id}", response_model=EntryOut, summary="Get entry by id")
def get_entry(entry_id: int, username: str = Depends(get_current_user)):
    us = _user_store(username)
    entry = _find_entry(us, entry_id)
    if not entry:
        raise ApiError("not_found", "entry not found", 404)
    return entry


@router.patch("/{entry_id}", response_model=EntryOut, summary="Patch entry")
def patch_entry(
    entry_id: int, payload: EntryUpdate, username: str = Depends(get_current_user)
):
    us = _user_store(username)
    entry = _find_entry(us, entry_id)
    if not entry:
        raise ApiError("not_found", "entry not found", 404)

    if payload.title is not None:
        entry["title"] = payload.title
    if payload.kind is not None:
        entry["kind"] = payload.kind
    if payload.link is not None:
        entry["link"] = str(payload.link)
    if payload.status is not None:
        entry["status"] = payload.status
    return entry


@router.delete("/{entry_id}", status_code=204, summary="Delete entry")
def delete_entry(entry_id: int, username: str = Depends(get_current_user)):
    us = _user_store(username)
    entry = _find_entry(us, entry_id)
    if not entry:
        raise ApiError("not_found", "entry not found", 404)
    us["entries"] = [e for e in us["entries"] if e["id"] != entry_id]
    return Response(status_code=204)


__all__ = ["router", "_ENTRIES_DB"]
