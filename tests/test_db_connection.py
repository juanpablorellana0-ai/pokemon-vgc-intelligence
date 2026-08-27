"""Database connection test.

Requires a running MongoDB instance reachable via ``MONGO_URL``. The test
is skipped automatically if the server is not reachable so CI doesn't
fail on environments without Mongo.
"""
import os
import sys
from pathlib import Path
import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(BACKEND_DIR / ".env")

from db import get_db, close_client  # noqa: E402


@pytest.mark.asyncio
async def test_mongo_ping():
    if not os.environ.get("MONGO_URL"):
        pytest.skip("MONGO_URL not configured")
    try:
        db = get_db()
        result = await db.command("ping")
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"Mongo not reachable: {exc}")
    else:
        assert result.get("ok") == 1
    finally:
        await close_client()
