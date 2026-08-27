"""API surface smoke tests.

Confirms every foundational resource is registered. In Phase 2B the
data endpoints require an active Showdown import — this suite only
covers routing/wiring; live-data verification lives in
``test_showdown_import.py``.
"""
import sys
from pathlib import Path
import pytest
import httpx

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from server import app  # noqa: E402


@pytest.mark.asyncio
async def test_health_ok():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_sources_registry():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sources")
    assert r.status_code == 200
    body = r.json()
    keys = {s["key"] for s in body}
    expected = {
        "pikalytics", "munchstats", "replica_teams", "labmaus",
        "reportworm", "cut_explorer", "showdown", "vgc_guide",
    }
    assert expected.issubset(keys)
    assert all(s["implemented"] is False for s in body)


@pytest.mark.asyncio
async def test_api_root_ok():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "v1" in body["versions"]


@pytest.mark.asyncio
async def test_data_endpoints_registered():
    """Every data endpoint must be reachable (200 when data present, 503 when
    no active dataset). We just assert the router exists — no fake data."""
    transport = httpx.ASGITransport(app=app)
    paths = [
        "/api/v1/pokemon", "/api/v1/moves", "/api/v1/abilities",
        "/api/v1/items", "/api/v1/natures", "/api/v1/types",
        "/api/v1/types/chart", "/api/v1/formats", "/api/v1/rulesets",
        "/api/v1/regulations",
    ]
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        for p in paths:
            r = await ac.get(p)
            assert r.status_code in (200, 503), f"{p} → {r.status_code}"
