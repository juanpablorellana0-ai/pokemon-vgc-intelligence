"""Domain models for Showdown sync.

Persisted in Mongo collection ``showdown_sync_history``.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class SyncStatus(str, Enum):
    STARTED = "started"
    UP_TO_DATE = "up_to_date"
    FETCHED = "fetched"
    VALIDATED = "validated"
    TESTED = "tested"
    ACTIVATED = "activated"
    FAILED_FETCH = "failed_fetch"
    FAILED_VALIDATION = "failed_validation"
    FAILED_TESTS = "failed_tests"
    FAILED_LOCKED = "failed_locked"
    ROLLED_BACK = "rolled_back"


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ShowdownSyncHistory(BaseModel):
    id: str = Field(default_factory=_uuid)
    repositoryUrl: str
    branch: str
    previousCommit: Optional[str] = None
    newCommit: Optional[str] = None
    startedAt: datetime = Field(default_factory=_now)
    completedAt: Optional[datetime] = None
    duration_ms: Optional[int] = None
    status: SyncStatus
    recordsDiscovered: int = 0
    recordsImported: int = 0
    recordsUpdated: int = 0
    recordsRejected: int = 0
    validationErrors: list[str] = []
    testResults: dict = {}
    activated: bool = False
    errorMessage: Optional[str] = None
    importerVersion: str = "0.1.0"
    appVersion: str = "0.1.0"


class ShowdownActiveDataset(BaseModel):
    """Pointer to the currently active dataset and the rollback candidate."""
    activeCommit: Optional[str] = None
    activeDir: Optional[str] = None
    activatedAt: Optional[datetime] = None
    previousCommit: Optional[str] = None
    previousDir: Optional[str] = None
    rollbackAvailable: bool = False
