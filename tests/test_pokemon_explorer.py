"""Phase 3A — Pokemon Data Explorer API tests.

Live-data tests against the active Showdown import in ``test_database``
(same pattern as ``test_showdown_import.py``). Skipped when no active
import exists. All assertion values are read from the canonical dataset
itself — nothing is hardcoded beyond well-known identifiers.
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


# ---------- listing & pagination ----------

@pytest.mark.asyncio
async def test_list_pagination_metadata(client, active_import):
    r = await client.get("/api/v1/pokemon", params={"limit": 10, "offset": 0})
    assert r.status_code == 200
    body = r.json()
    for key in ("total", "limit", "offset", "page", "pages", "import_id", "items"):
        assert key in body, f"missing pagination key: {key}"
    assert body["limit"] == 10
    assert body["page"] == 1
    assert body["pages"] == (body["total"] + 9) // 10
    assert len(body["items"]) == 10
    assert body["import_id"] == active_import


@pytest.mark.asyncio
async def test_list_pages_do_not_overlap(client, active_import):
    r1 = await client.get("/api/v1/pokemon", params={"limit": 5, "offset": 0})
    r2 = await client.get("/api/v1/pokemon", params={"limit": 5, "offset": 5})
    ids1 = {p["showdown_id"] for p in r1.json()["items"]}
    ids2 = {p["showdown_id"] for p in r2.json()["items"]}
    assert ids1 and ids2
    assert ids1.isdisjoint(ids2)
    assert r2.json()["page"] == 2


@pytest.mark.asyncio
async def test_list_last_page_boundary(client, active_import):
    total = (await client.get("/api/v1/pokemon", params={"limit": 1})).json()["total"]
    r = await client.get("/api/v1/pokemon", params={"limit": 50, "offset": (total // 50) * 50})
    body = r.json()
    assert r.status_code == 200
    assert 0 < len(body["items"]) <= 50
    # beyond the end → empty items, not an error
    r2 = await client.get("/api/v1/pokemon", params={"limit": 50, "offset": total + 100})
    assert r2.status_code == 200
    assert r2.json()["items"] == []


@pytest.mark.asyncio
async def test_invalid_pagination_rejected(client):
    for params in ({"limit": 0}, {"limit": 501}, {"offset": -1}, {"limit": "abc"}):
        r = await client.get("/api/v1/pokemon", params=params)
        assert r.status_code == 422, f"{params} → {r.status_code}"


# ---------- search ----------

@pytest.mark.asyncio
async def test_search_case_insensitive(client, active_import):
    upper = (await client.get("/api/v1/pokemon", params={"q": "Gholdengo"})).json()
    lower = (await client.get("/api/v1/pokemon", params={"q": "gholdengo"})).json()
    assert upper["total"] == lower["total"] >= 1
    assert {p["showdown_id"] for p in upper["items"]} == {p["showdown_id"] for p in lower["items"]}
    assert any(p["showdown_id"] == "gholdengo" for p in upper["items"])


@pytest.mark.asyncio
async def test_search_partial_match(client, active_import):
    body = (await client.get("/api/v1/pokemon", params={"q": "ghold"})).json()
    assert body["total"] >= 1
    assert all("ghold" in p["slug"].lower() or "ghold" in p["name"].lower() for p in body["items"])


@pytest.mark.asyncio
async def test_search_no_results(client, active_import):
    body = (await client.get("/api/v1/pokemon", params={"q": "zzzznotapokemon"})).json()
    assert body["total"] == 0
    assert body["items"] == []
    assert body["pages"] == 0


@pytest.mark.asyncio
async def test_search_regex_input_is_safe(client, active_import):
    # regex metacharacters must be escaped, not evaluated
    for q in ("(", ".*", "a|b", "[", "\\"):
        r = await client.get("/api/v1/pokemon", params={"q": q})
        assert r.status_code == 200, f"q={q!r} → {r.status_code}"
    # ".*" escaped means literal — should match nothing, not everything
    body = (await client.get("/api/v1/pokemon", params={"q": ".*"})).json()
    assert body["total"] == 0


@pytest.mark.asyncio
async def test_search_ordering_is_deterministic(client, active_import):
    a = (await client.get("/api/v1/pokemon", params={"q": "mew", "limit": 50})).json()
    b = (await client.get("/api/v1/pokemon", params={"q": "mew", "limit": 50})).json()
    assert [p["showdown_id"] for p in a["items"]] == [p["showdown_id"] for p in b["items"]]
    nums = [p["num"] for p in a["items"]]
    assert nums == sorted(nums)


# ---------- filters ----------

@pytest.mark.asyncio
async def test_filter_by_type(client, active_import):
    body = (await client.get("/api/v1/pokemon", params={"type": "Steel", "limit": 500})).json()
    assert body["total"] >= 1
    assert all("Steel" in p["types"] for p in body["items"])
    # case-insensitive
    lower = (await client.get("/api/v1/pokemon", params={"type": "steel", "limit": 1})).json()
    assert lower["total"] == body["total"]


@pytest.mark.asyncio
async def test_filter_by_ability(client, active_import):
    body = (await client.get("/api/v1/pokemon", params={"ability": "Intimidate", "limit": 500})).json()
    assert body["total"] >= 1
    ids = {p["showdown_id"] for p in body["items"]}
    assert "incineroar" in ids
    for p in body["items"]:
        assert "Intimidate" in set((p.get("abilities") or {}).values()), p["showdown_id"]


@pytest.mark.asyncio
async def test_filter_only_base(client, active_import):
    body = (await client.get("/api/v1/pokemon", params={"only_base": "true", "limit": 500})).json()
    assert body["total"] >= 1
    assert all(p["is_base"] is True for p in body["items"])


@pytest.mark.asyncio
async def test_filters_combine_with_search(client, active_import):
    body = (
        await client.get(
            "/api/v1/pokemon",
            params={"q": "gh", "type": "Ghost", "only_base": "true", "limit": 500},
        )
    ).json()
    for p in body["items"]:
        assert "Ghost" in p["types"]
        assert p["is_base"] is True


@pytest.mark.asyncio
async def test_special_entries_excluded_by_default(client, active_import):
    default = (await client.get("/api/v1/pokemon", params={"limit": 5})).json()
    assert all(p["num"] >= 1 for p in default["items"])
    withspecial = (
        await client.get("/api/v1/pokemon", params={"limit": 5, "include_special": "true"})
    ).json()
    assert withspecial["total"] > default["total"]
    # non-standard entries stay reachable through detail
    r = await client.get("/api/v1/pokemon/missingno")
    assert r.status_code == 200


# ---------- detail ----------

@pytest.mark.asyncio
async def test_detail_by_slug_and_num_agree(client, active_import):
    by_slug = (await client.get("/api/v1/pokemon/gholdengo")).json()
    by_num = (await client.get(f"/api/v1/pokemon/{by_slug['num']}")).json()
    assert by_num["showdown_id"] == by_slug["showdown_id"] == "gholdengo"
    assert by_slug["types"] == by_num["types"]
    assert "learnset" in by_slug and isinstance(by_slug["learnset"], dict)


@pytest.mark.asyncio
async def test_detail_not_found(client, active_import):
    r = await client.get("/api/v1/pokemon/notarealpokemon123x")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"]


@pytest.mark.asyncio
async def test_detail_matches_canonical_dataset(client, db, active_import):
    """API detail must mirror the canonical Showdown document exactly."""
    canonical = await db["sd_pokemon"].find_one(
        {"import_id": active_import, "showdown_id": "incineroar"}, {"_id": 0, "import_id": 0},
    )
    assert canonical, "incineroar missing from canonical dataset"
    api = (await client.get("/api/v1/pokemon/incineroar")).json()
    for field in ("showdown_id", "num", "name", "types", "base_stats", "abilities", "is_base"):
        assert api[field] == canonical[field], f"field mismatch: {field}"


# ---------- moves & abilities subroutes ----------

@pytest.mark.asyncio
async def test_pokemon_abilities_resolved(client, db, active_import):
    body = (await client.get("/api/v1/pokemon/incineroar/abilities")).json()
    canonical = await db["sd_pokemon"].find_one(
        {"import_id": active_import, "showdown_id": "incineroar"},
    )
    slots = canonical["abilities"]
    assert body["pokemon"] == "incineroar"
    assert body["total"] == len(slots)
    by_slot = {i["slot"]: i for i in body["items"]}
    for slot, name in slots.items():
        assert by_slot[slot]["name"] == name
        assert by_slot[slot]["is_hidden"] == (slot == "H")
        resolved = by_slot[slot]["ability"]
        assert resolved is not None and resolved["name"] == name


@pytest.mark.asyncio
async def test_pokemon_moves_resolved_from_learnset(client, db, active_import):
    body = (await client.get("/api/v1/pokemon/gholdengo/moves")).json()
    ls = await db["sd_learnsets"].find_one(
        {"import_id": active_import, "showdown_id": "gholdengo"},
    )
    learn_map = ls["moves"]
    assert body["pokemon"] == "gholdengo"
    assert body["total"] + len(body["unresolved"]) == len(learn_map)
    for m in body["items"]:
        assert m["showdown_id"] in learn_map
        assert m["learn_sources"] == learn_map[m["showdown_id"]]
        assert "name" in m and "type" in m and "category" in m
    names = [m["name"] for m in body["items"]]
    assert names == sorted(names)


@pytest.mark.asyncio
async def test_pokemon_moves_not_found(client, active_import):
    r = await client.get("/api/v1/pokemon/notarealpokemon123x/moves")
    assert r.status_code == 404
    r2 = await client.get("/api/v1/pokemon/notarealpokemon123x/abilities")
    assert r2.status_code == 404
