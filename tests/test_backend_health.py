"""Backend health check tests.

These tests exercise the FastAPI application in-process via
``httpx.ASGITransport`` — no live network, no forked processes. They
validate that the top-level and versioned health endpoints respond.
"""
import sys
from pathlib import Path
import pytest
import httpx

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from server import app  # noqa: E402


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
async def test_v1_health_ok():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
