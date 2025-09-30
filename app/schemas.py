from __future__ import annotations

from typing import Literal, Optional

from pydantic import AnyHttpUrl, BaseModel, field_validator

EntryKind = Literal["book", "article", "course", "video", "other"]
EntryStatus = Literal["planned", "in_progress", "completed", "dropped"]


class EntryCreate(BaseModel):
    title: str
    kind: EntryKind
    link: Optional[AnyHttpUrl] = None
    status: EntryStatus = "planned"


class EntryUpdate(BaseModel):
    title: Optional[str] = None
    kind: Optional[EntryKind] = None
    link: Optional[AnyHttpUrl] = None
    status: Optional[EntryStatus] = None

    @field_validator("title")
    @classmethod
    def _title_not_empty(cls, v: str | None):
        if v is not None and not v.strip():
            raise ValueError("title cannot be empty")
        return v


class EntryOut(BaseModel):
    id: int
    title: str
    kind: EntryKind
    link: Optional[str] = None
    status: EntryStatus

    class Config:
        from_attributes = True
