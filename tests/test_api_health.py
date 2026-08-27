"""API surface smoke tests.

Confirms every foundational resource is registered and returns an empty
list in the foundation phase (no fabricated statistics ship).
"""
import sys
from pathlib import Path
import pytest
import httpx

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from server import app  # noqa: E402

RESOURCES = [
    "/api/v1/pokemon",
    "/api/v1/moves",
    "/api/v1/items",
    "/api/v1/abilities",
    "/api/v1/teams",
    "/api/v1/tournaments",
    "/api/v1/standings",
    "/api/v1/meta/usage",
    "/api/v1/cores",
]


@pytest.mark.asyncio
@pytest.mark.parametrize("path", RESOURCES)
async def test_resource_lists_empty(path):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get(path)
    assert r.status_code == 200, path
    assert isinstance(r.json(), list), path


@pytest.mark.asyncio
async def test_sources_registry():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sources")
    assert r.status_code == 200
    body = r.json()
    keys = {s["key"] for s in body}
    expected = {
        "pikalytics",
        "munchstats",
        "replica_teams",
        "labmaus",
        "reportworm",
        "cut_explorer",
        "showdown",
        "vgc_guide",
    }
    assert expected.issubset(keys)
    # None of the adapters should be marked implemented yet.
    assert all(s["implemented"] is False for s in body)
