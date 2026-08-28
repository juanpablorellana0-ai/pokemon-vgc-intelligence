"""Phase 3A addendum — Pokemon image resolver tests.

Unit tests for the sprite URL builder plus live-data API tests verifying
image references in list/detail responses. No external network calls.
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
import httpx
from motor.motor_asyncio import AsyncIOMotorClient

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_DIR))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "test_database")

from server import app  # noqa: E402
from sprites import FALLBACK_SPRITE_URL, SPRITE_BASE, attach_image_urls, sprite_id  # noqa: E402


@pytest_asyncio.fixture
async def db():
    client = AsyncIOMotorClient(os.environ["MONGO_URL"])
    yield client[os.environ["DB_NAME"]]
    client.close()


@pytest_asyncio.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def active_import(db):
    doc = await db["showdown_pointers"].find_one({"_id": "showdown_active_dataset"})
    imp = (doc or {}).get("activeImportId")
    if not imp:
        pytest.skip("no active Showdown import — run /admin/showdown/sync first")
    return imp


# ---------- resolver unit tests ----------

def test_sprite_id_plain_species():
    assert sprite_id({"showdown_id": "gholdengo", "base_species_name": None, "forme": None}) == "gholdengo"


def test_sprite_id_forme_specific():
    assert sprite_id({"showdown_id": "venusaurmega", "base_species_name": "Venusaur", "forme": "Mega"}) == "venusaur-mega"
    assert sprite_id({"showdown_id": "venusaurgmax", "base_species_name": "Venusaur", "forme": "Gmax"}) == "venusaur-gmax"
    assert sprite_id({"showdown_id": "urshifurapidstrike", "base_species_name": "Urshifu", "forme": "Rapid-Strike"}) == "urshifu-rapidstrike"


def test_attach_image_urls_shape():
    doc = attach_image_urls({"showdown_id": "pikachu", "base_species_name": None, "forme": None})
    assert doc["image_url"] == f"{SPRITE_BASE}/gen5/pikachu.png"
    assert doc["image_fallback_url"] == FALLBACK_SPRITE_URL
    assert FALLBACK_SPRITE_URL.endswith("/gen5/0.png")


def test_missing_image_still_gets_fallback_reference():
    # a species with no real sprite (e.g. MissingNo.) still resolves to a URL
    # + fallback; the frontend swaps to the fallback on load error.
    doc = attach_image_urls({"showdown_id": "missingno", "base_species_name": None, "forme": None})
    assert doc["image_url"].endswith("/missingno.png")
    assert doc["image_fallback_url"] == FALLBACK_SPRITE_URL


# ---------- API integration ----------

@pytest.mark.asyncio
async def test_list_items_carry_image_reference(client, active_import):
    body = (await client.get("/api/v1/pokemon", params={"limit": 20})).json()
    assert body["items"]
    for p in body["items"]:
        assert p["image_url"].startswith(f"{SPRITE_BASE}/gen5/")
        assert p["image_url"].endswith(".png")
        assert p["image_fallback_url"] == FALLBACK_SPRITE_URL


@pytest.mark.asyncio
async def test_detail_image_for_base_species(client, active_import):
    body = (await client.get("/api/v1/pokemon/venusaur")).json()
    assert body["image_url"] == f"{SPRITE_BASE}/gen5/venusaur.png"


@pytest.mark.asyncio
async def test_detail_image_is_forme_specific(client, active_import):
    base = (await client.get("/api/v1/pokemon/venusaur")).json()
    mega = (await client.get("/api/v1/pokemon/venusaurmega")).json()
    gmax = (await client.get("/api/v1/pokemon/venusaurgmax")).json()
    assert mega["image_url"] == f"{SPRITE_BASE}/gen5/venusaur-mega.png"
    assert gmax["image_url"] == f"{SPRITE_BASE}/gen5/venusaur-gmax.png"
    assert len({base["image_url"], mega["image_url"], gmax["image_url"]}) == 3


@pytest.mark.asyncio
async def test_every_forme_resolves_to_distinct_or_valid_id(client, db, active_import):
    """Forme documents must never reuse the plain base-species sprite id."""
    cursor = db["sd_pokemon"].find(
        {"import_id": active_import, "forme": {"$ne": None}, "num": {"$gte": 1}},
        {"_id": 0, "showdown_id": 1, "base_species_name": 1, "forme": 1},
    ).limit(200)
    async for doc in cursor:
        sid = sprite_id(doc)
        assert "-" in sid, f"forme {doc['showdown_id']} resolved to non-forme sprite {sid}"
