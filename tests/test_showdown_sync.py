"""Tests for the Showdown sync infrastructure.

Every external side effect (git ls-remote, clone, TS parsing) is
monkeypatched so tests stay offline and fast. Each test uses an
isolated temp Mongo database.
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
    yield ShowdownSyncService(db)


async def _await(value):
    return value


def _stub_pipeline(svc, monkeypatch, *, remote_sha, parsed=None,
                   fetch_error=None, tests_ok=True):
    """Wire up minimal stubs so ``sync`` runs without touching disk/net."""
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await(remote_sha))

    async def _fetch(_commit):
        if fetch_error:
            raise fetch_error
        return f"/tmp/stub-{remote_sha[:8]}"

    async def _parse(_dir):
        return parsed if parsed is not None else {}

    async def _run_tests(_dir, _import_id=None):
        return {"passed": tests_ok, "stub": True}

    monkeypatch.setattr(svc, "_fetch", _fetch)
    monkeypatch.setattr(svc, "_parse", _parse)
    monkeypatch.setattr(svc, "_run_tests", _run_tests)


# ---------------------------------------------------------------------------
# Check semantics
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_check_reports_up_to_date_when_active_matches_remote(svc, monkeypatch):
    sha = "a" * 40
    monkeypatch.setattr(svc, "_ls_remote", lambda: _await(sha))
    from ingestion.showdown.models import ShowdownActiveDataset
    ptr = ShowdownActiveDataset(
        activeCommit=sha, activeDir="/tmp/x",
        activatedAt=datetime.now(timezone.utc), rollbackAvailable=False,
    ).model_dump()
    ptr["_id"] = "showdown_active_dataset"
    await svc.db["showdown_pointers"].insert_one(ptr)
    result = await svc.check()
    assert result["updateAvailable"] is False
    assert result["remoteCommit"] == sha


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
    _stub_pipeline(svc, monkeypatch, remote_sha=sha)
    h = await svc.sync()
    assert h.status == SyncStatus.ACTIVATED
    assert h.activated is True
    assert h.newCommit == sha
    active = await svc.get_active()
    assert active.activeCommit == sha


# ---------------------------------------------------------------------------
# Failed download preserves active
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_sync_failed_fetch_preserves_active(svc, monkeypatch):
    _stub_pipeline(svc, monkeypatch, remote_sha="d" * 40)
    ok = await svc.sync()
    assert ok.status == SyncStatus.ACTIVATED

    _stub_pipeline(svc, monkeypatch, remote_sha="e" * 40,
                   fetch_error=RuntimeError("network dead"))
    h = await svc.sync()
    assert h.status == SyncStatus.FAILED_FETCH
    active = await svc.get_active()
    assert active.activeCommit == "d" * 40


# ---------------------------------------------------------------------------
# Validation failure preserves active
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_sync_failed_validation_preserves_active(svc, monkeypatch):
    _stub_pipeline(svc, monkeypatch, remote_sha="f" * 40)

    # Simulate a parser crash — the service converts it to a validation error.
    async def _parse_boom(_dir):
        raise RuntimeError("bad schema")
    monkeypatch.setattr(svc, "_parse", _parse_boom)

    h = await svc.sync()
    assert h.status == SyncStatus.FAILED_VALIDATION
    assert h.validationErrors
    active = await svc.get_active()
    assert active.activeCommit is None


# ---------------------------------------------------------------------------
# Compatibility test failure preserves active
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_sync_failed_tests_preserves_active(svc, monkeypatch):
    _stub_pipeline(svc, monkeypatch, remote_sha="9" * 40, tests_ok=False)
    h = await svc.sync()
    assert h.status == SyncStatus.FAILED_TESTS
    assert h.activated is False
    active = await svc.get_active()
    assert active.activeCommit is None


# ---------------------------------------------------------------------------
# Rollback
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rollback_restores_previous(svc, monkeypatch):
    _stub_pipeline(svc, monkeypatch, remote_sha="1" * 40)
    await svc.sync()
    _stub_pipeline(svc, monkeypatch, remote_sha="2" * 40)
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
# Concurrent-sync protection
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_concurrent_sync_returns_locked(svc, db, monkeypatch):
    assert await sd_lock.acquire(db, owner="external-worker")
    _stub_pipeline(svc, monkeypatch, remote_sha="7" * 40)
    h = await svc.sync()
    assert h.status == SyncStatus.FAILED_LOCKED
    assert "another sync" in (h.errorMessage or "")
    await sd_lock.release(db)


@pytest.mark.asyncio
async def test_duplicate_sync_requests_serialize(svc, monkeypatch):
    _stub_pipeline(svc, monkeypatch, remote_sha="3" * 40)
    h1 = await svc.sync()
    h2 = await svc.sync()
    assert h1.status == SyncStatus.ACTIVATED
    assert h2.status == SyncStatus.UP_TO_DATE


# ---------------------------------------------------------------------------
# Admin endpoint auth
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
