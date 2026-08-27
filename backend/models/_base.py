"""Shared base class for VGC domain models."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel, Field


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class VGCBase(BaseModel):
    id: str = Field(default_factory=_uuid)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
