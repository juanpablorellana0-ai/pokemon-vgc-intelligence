"""Shared pytest fixtures.

pytest-asyncio creates a fresh event loop per test. Motor clients are
bound to the loop they were created on, so we reset the module-level
singleton between tests to avoid ``Event loop is closed`` errors.
"""
import sys
from pathlib import Path
import pytest_asyncio

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from db import close_client  # noqa: E402


@pytest_asyncio.fixture(autouse=True)
async def _reset_mongo_client():
    yield
    await close_client()
