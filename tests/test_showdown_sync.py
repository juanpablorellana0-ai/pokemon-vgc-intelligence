"""Tests for the Showdown sync infrastructure.

All external calls (git ls-remote, filesystem clones) are monkeypatched
so tests run offline. Each test uses an isolated temp Mongo database.
"""
from __future__ import annotations
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime, timezone

import pytest
import pytest_asyncio
import httpx

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Configure env BEFORE importing modules that read env at import time.
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "test_database")
os.environ["ADMIN_TOKEN"] = "test-admin-token"
os.environ["SHOWDOWN_DATASETS_DIR"] = "/tmp/vgc_test_datasets"

from motor.motor_asyncio import AsyncIOMotorClient  # noqa: E402

from ingestion.showdown import ShowdownSyncService  # noqa: E402
from ingestion.showdown.models import SyncStatus  # noqa: E402
from ingestion.showdown import lock as sd_lock  # noqa: E402
from server import app  # noqa: E402


@pytest_asyncio.fixture
async def db():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    name = f"vgc_test_{uuid.uuid4().hex[:8]}"
    yield client[name]
    await client.drop_database(name)
    client.close()


@pytest_asyncio.fixture
async def svc(db):
    service = ShowdownSyncService(db)
    yield service


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
async def _await(value):
    """Return ``value`` from an awaitable — used to stub async methods."""
    return value


# ---------------------------------------------------------------------------
# Detecting unchanged / new commits (check endpoint semantics)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_check_reports_up_to_date_when_active_matches_remote(svc, monkeypatch):
    sha = "a" * 40
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await(sha))
    from ingestion.showdown.models import ShowdownActiveDataset
    await svc._write_active(ShowdownActiveDataset(
        activeCommit=sha, activeDir="/tmp/x",
        activatedAt=datetime.now(timezone.utc), rollbackAvailable=False,
    ))
    result = await svc.check()
    assert result["updateAvailable"] is False
    assert result["remoteCommit"] == sha
    assert result["activeCommit"] == sha


@pytest.mark.asyncio
async def test_check_reports_update_available_when_new_commit(svc, monkeypatch):
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await("b" * 40))
    result = await svc.check()
    assert result["updateAvailable"] is True
    assert result["remoteCommit"] == "b" * 40
    assert result["activeCommit"] is None


# ---------------------------------------------------------------------------
# Successful activation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_sync_activates_when_all_stages_pass(svc, monkeypatch):
    sha = "c" * 40
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await(sha))
    h = await svc.sync()
    assert h.status == SyncStatus.ACTIVATED
    assert h.activated is True
    assert h.newCommit == sha
    active = await svc.get_active()
    assert active.activeCommit == sha


# ---------------------------------------------------------------------------
# Failed download — active dataset must remain unchanged
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_sync_failed_fetch_preserves_active(svc, monkeypatch):
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await("d" * 40))
    ok = await svc.sync()
    assert ok.status == SyncStatus.ACTIVATED

    monkeypatch.setattr(svc, "_ls_remote", lambda: _await("e" * 40))
    async def _boom(commit): raise RuntimeError("network dead")
    monkeypatch.setattr(svc, "_fetch", _boom)
    h = await svc.sync()
    assert h.status == SyncStatus.FAILED_FETCH
    active = await svc.get_active()
    assert active.activeCommit == "d" * 40


# ---------------------------------------------------------------------------
# Invalid data / validation failure
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_sync_failed_validation_preserves_active(svc, monkeypatch):
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await("f" * 40))
    async def _bad_validate(_dir): return ["schema mismatch"]
    monkeypatch.setattr(svc, "_validate", _bad_validate)
    h = await svc.sync()
    assert h.status == SyncStatus.FAILED_VALIDATION
    assert h.validationErrors == ["schema mismatch"]
    active = await svc.get_active()
    assert active.activeCommit is None


# ---------------------------------------------------------------------------
# Compatibility test failure
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_sync_failed_tests_preserves_active(svc, monkeypatch):
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await("9" * 40))
    async def _bad_tests(_dir): return {"passed": False, "reason": "regression"}
    monkeypatch.setattr(svc, "_run_tests", _bad_tests)
    h = await svc.sync()
    assert h.status == SyncStatus.FAILED_TESTS
    assert h.activated is False
    active = await svc.get_active()
    assert active.activeCommit is None


# ---------------------------------------------------------------------------
# Rollback restores previous version
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rollback_restores_previous(svc, monkeypatch):
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await("1" * 40))
    await svc.sync()
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await("2" * 40))
    await svc.sync()
    active = await svc.get_active()
    assert active.activeCommit == "2" * 40
    assert active.rollbackAvailable is True

    result = await svc.rollback()
    assert result["rolled_back"] is True
    active = await svc.get_active()
    assert active.activeCommit == "1" * 40


@pytest.mark.asyncio
async def test_rollback_no_previous(svc):
    result = await svc.rollback()
    assert result["rolled_back"] is False


# ---------------------------------------------------------------------------
# Duplicate / concurrent sync protection
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_concurrent_sync_returns_locked(svc, db, monkeypatch):
    assert await sd_lock.acquire(db, owner="external-worker")
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await("7" * 40))
    h = await svc.sync()
    assert h.status == SyncStatus.FAILED_LOCKED
    assert "another sync" in (h.errorMessage or "")
    await sd_lock.release(db)


@pytest.mark.asyncio
async def test_duplicate_sync_requests_serialize(svc, monkeypatch):
    """Two consecutive sync calls both complete without corruption."""
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await("3" * 40))
    h1 = await svc.sync()
    h2 = await svc.sync()  # already up-to-date
    assert h1.status == SyncStatus.ACTIVATED
    assert h2.status == SyncStatus.UP_TO_DATE


# ---------------------------------------------------------------------------
# Admin endpoints are protected
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_admin_endpoints_require_token():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r_missing = await ac.get("/api/v1/admin/showdown/status")
        r_wrong = await ac.get(
            "/api/v1/admin/showdown/status",
            headers={"X-Admin-Token": "nope"},
        )
        r_ok = await ac.get(
            "/api/v1/admin/showdown/status",
            headers={"X-Admin-Token": "test-admin-token"},
        )
    assert r_missing.status_code == 401
    assert r_wrong.status_code == 401
    assert r_ok.status_code == 200


@pytest.mark.asyncio
async def test_admin_endpoints_disabled_without_token_env(monkeypatch):
    monkeypatch.delenv("ADMIN_TOKEN", raising=False)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get(
            "/api/v1/admin/showdown/status",
            headers={"X-Admin-Token": "any"},
        )
    assert r.status_code == 503
