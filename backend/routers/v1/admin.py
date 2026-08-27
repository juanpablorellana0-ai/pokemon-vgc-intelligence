"""Admin-only endpoints for Showdown sync.

Protected by a shared secret sent via the ``X-Admin-Token`` header. The
token is read from ``ADMIN_TOKEN`` env var — if unset, all admin routes
return 503 so nothing is accidentally public.
"""
from __future__ import annotations
import os
from fastapi import APIRouter, Depends, HTTPException, Header, status

from db import get_db
from ingestion.showdown import ShowdownSyncService

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(x_admin_token: str | None = Header(default=None)) -> None:
    expected = os.environ.get("ADMIN_TOKEN")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="admin endpoints disabled: ADMIN_TOKEN not configured",
        )
    if not x_admin_token or x_admin_token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing X-Admin-Token",
        )


def _service() -> ShowdownSyncService:
    return ShowdownSyncService(get_db())


@router.get("/showdown/status", dependencies=[Depends(require_admin)])
async def showdown_status():
    return await _service().status()


@router.post("/showdown/check", dependencies=[Depends(require_admin)])
async def showdown_check():
    return await _service().check()


@router.post("/showdown/sync", dependencies=[Depends(require_admin)])
async def showdown_sync(force: bool = False):
    history = await _service().sync(force=force)
    return history.model_dump()


@router.post("/showdown/rollback", dependencies=[Depends(require_admin)])
async def showdown_rollback():
    return await _service().rollback()
