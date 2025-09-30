from __future__ import annotations

from typing import Any, Dict, Literal, Optional
import sqlite3

from fastapi import APIRouter, HTTPException
from pydantic import AnyHttpUrl, BaseModel, field_validator

router = APIRouter(prefix="/entries", tags=["entries"])

EntryKind = Literal["book", "article", "course", "video", "other"]
EntryStatus = Literal["planned", "in_progress", "completed", "dropped"]


class EntryCreate(BaseModel):
    title: str
    kind: EntryKind
    link: Optional[AnyHttpUrl] = None
    status: EntryStatus = "planned"

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


# Database functions
def get_db():
    conn = sqlite3.connect("reading.db")
    conn.row_factory = sqlite3.Row
    return conn


def _find_entry(entry_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db()
    entry = conn.execute(
        "SELECT * FROM reading_entries WHERE id = ?", (entry_id,)
    ).fetchone()
    conn.close()
    return dict(entry) if entry else None


@router.post("", response_model=EntryOut, summary="Create reading entry")
def create_entry(payload: EntryCreate):
    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO reading_entries (title, kind, link, status) VALUES (?, ?, ?, ?)",
            (payload.title, payload.kind, str(payload.link) if payload.link else None, payload.status)
        )
        conn.commit()

        new_id = cursor.lastrowid
        created_entry = conn.execute(
            "SELECT * FROM reading_entries WHERE id = ?", (new_id,)
        ).fetchone()
        conn.close()

        return dict(created_entry)
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")


@router.get("", response_model=list[EntryOut], summary="List entries (with ?status=)")
def list_entries(status: Optional[EntryStatus] = None):
    conn = get_db()

    if status:
        entries = conn.execute(
            "SELECT * FROM reading_entries WHERE status = ?", (status,)
        ).fetchall()
    else:
        entries = conn.execute("SELECT * FROM reading_entries").fetchall()

    conn.close()
    return [dict(entry) for entry in entries]


@router.get("/{entry_id}", response_model=EntryOut, summary="Get entry by id")
def get_entry(entry_id: int):
    entry = _find_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


@router.put("/{entry_id}", response_model=EntryOut, summary="Update entry")
def update_entry(entry_id: int, payload: EntryUpdate):
    conn = get_db()

    # Check if entry exists
    existing = _find_entry(entry_id)
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Entry not found")

    # Build update fields
    update_fields = {}
    if payload.title is not None:
        update_fields["title"] = payload.title
    if payload.kind is not None:
        update_fields["kind"] = payload.kind
    if payload.link is not None:
        update_fields["link"] = str(payload.link)
    if payload.status is not None:
        update_fields["status"] = payload.status

    if not update_fields:
        conn.close()
        raise HTTPException(status_code=422, detail="No fields to update")

    # Build SQL query
    set_clause = ", ".join([f"{field} = ?" for field in update_fields])
    values = list(update_fields.values())
    values.append(entry_id)

    try:
        conn.execute(
            f"UPDATE reading_entries SET {set_clause} WHERE id = ?",
            values
        )
        conn.commit()

        updated_entry = conn.execute(
            "SELECT * FROM reading_entries WHERE id = ?", (entry_id,)
        ).fetchone()
        conn.close()

        return dict(updated_entry)
    except sqlite3.IntegrityError as e:
        conn.close()
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")


@router.delete("/{entry_id}", summary="Delete entry")
def delete_entry(entry_id: int):
    conn = get_db()

    existing = _find_entry(entry_id)
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Entry not found")

    conn.execute("DELETE FROM reading_entries WHERE id = ?", (entry_id,))
    conn.commit()
    conn.close()

    return {"message": "Entry deleted successfully"}


@router.get("/stats/summary", summary="Get reading statistics")
def get_stats():
    conn = get_db()

    total = conn.execute("SELECT COUNT(*) as count FROM reading_entries").fetchone()["count"]

    by_status = conn.execute(
        "SELECT status, COUNT(*) as count FROM reading_entries GROUP BY status"
    ).fetchall()

    by_kind = conn.execute(
        "SELECT kind, COUNT(*) as count FROM reading_entries GROUP BY kind"
    ).fetchall()

    conn.close()

    return {
        "total_entries": total,
        "by_status": {row["status"]: row["count"] for row in by_status},
        "by_kind": {row["kind"]: row["count"] for row in by_kind}
    }


__all__ = ["router"]