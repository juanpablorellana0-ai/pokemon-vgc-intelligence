"""Pokemon read API — Phase 3A Pokemon Data Explorer.

All responses come exclusively from the canonical Showdown import
(``sd_*`` collections) scoped to the active ``import_id``. Nothing is
fabricated here; fields absent from the canonical dataset (e.g.
generation, per-Pokemon format legality) are intentionally not exposed.
"""
from __future__ import annotations
import re

from fastapi import APIRouter, HTTPException, Query
from db import get_db
from ._query import paged_list, require_active_import

router = APIRouter(prefix="/pokemon", tags=["pokemon"])

# Showdown ability slots: 0/1 regular, H hidden, S special (event).
ABILITY_SLOTS = ("0", "1", "H", "S")


def _to_showdown_id(value: str) -> str:
    """Showdown's toID(): lowercase, strip every non-alphanumeric char."""
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _exact_ci(value: str) -> dict:
    """Case-insensitive exact match, with user input regex-escaped."""
    return {"$regex": f"^{re.escape(value)}$", "$options": "i"}


async def _find_pokemon(id: str, projection: dict | None = None) -> tuple[str, dict]:
    """Resolve a Pokemon by showdown_id/slug/name or dex number.

    Prefers the base species when several formes share a dex number.
    Raises 404 when nothing matches the active import.
    """
    imp = await require_active_import(get_db())
    q: dict = {"import_id": imp}
    if id.isdigit():
        q["num"] = int(id)
    else:
        q["showdown_id"] = _to_showdown_id(id)
    # Mongo forbids mixing inclusion and exclusion: use pure inclusion when a
    # field subset is requested, otherwise exclude bookkeeping fields.
    proj = {"_id": 0, **projection} if projection else {"_id": 0, "import_id": 0}
    docs = await (
        get_db()["sd_pokemon"]
        .find(q, proj)
        .sort([("is_base", -1), ("showdown_id", 1)])
        .limit(1)
        .to_list(1)
    )
    if not docs:
        raise HTTPException(status_code=404, detail=f"pokemon not found: {id}")
    return imp, docs[0]


@router.get("")
async def list_pokemon(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    only_base: bool = Query(False, description="Only base species (exclude forms)"),
    q: str | None = Query(None, description="Case-insensitive substring on name/slug"),
    type: str | None = Query(None, description="Filter by type (e.g. Steel)"),
    ability: str | None = Query(None, description="Filter by ability name (e.g. Intimidate)"),
    include_special: bool = Query(
        False,
        description="Include non-standard entries (num <= 0: CAP, Pokestar Studios, MissingNo.)",
    ),
):
    clauses: list[dict] = []
    if not include_special:
        clauses.append({"num": {"$gte": 1}})
    if only_base:
        clauses.append({"is_base": True})
    if q:
        esc = re.escape(q)
        clauses.append({"$or": [
            {"slug": {"$regex": esc.lower(), "$options": "i"}},
            {"name": {"$regex": esc, "$options": "i"}},
        ]})
    if type:
        clauses.append({"types": _exact_ci(type)})
    if ability:
        clauses.append({"$or": [
            {f"abilities.{slot}": _exact_ci(ability)} for slot in ABILITY_SLOTS
        ]})
    filt: dict = {}
    if len(clauses) == 1:
        filt = clauses[0]
    elif clauses:
        filt = {"$and": clauses}
    return await paged_list(
        get_db(), "sd_pokemon",
        limit=limit, offset=offset,
        extra_filter=filt, sort=[("num", 1), ("name", 1)],
    )


@router.get("/{id}")
async def get_pokemon(id: str):
    imp, doc = await _find_pokemon(id)
    # attach learnset (raw canonical map: move id -> learn sources)
    ls = await get_db()["sd_learnsets"].find_one(
        {"import_id": imp, "showdown_id": doc["showdown_id"]},
        {"_id": 0, "import_id": 0},
    )
    doc["learnset"] = (ls or {}).get("moves", {})
    return doc


@router.get("/{id}/abilities")
async def get_pokemon_abilities(id: str):
    """The Pokemon's ability slots resolved against ``sd_abilities``."""
    imp, doc = await _find_pokemon(
        id, projection={"showdown_id": 1, "name": 1, "abilities": 1},
    )
    slots: dict = doc.get("abilities") or {}
    ability_ids = [_to_showdown_id(n) for n in slots.values()]
    resolved: dict[str, dict] = {}
    if ability_ids:
        found = await get_db()["sd_abilities"].find(
            {"import_id": imp, "showdown_id": {"$in": ability_ids}},
            {"_id": 0, "import_id": 0},
        ).to_list(len(ability_ids))
        resolved = {a["showdown_id"]: a for a in found}
    items = [
        {
            "slot": slot,
            "is_hidden": slot == "H",
            "name": slots[slot],
            "ability": resolved.get(_to_showdown_id(slots[slot])),
        }
        for slot in ABILITY_SLOTS if slot in slots
    ]
    return {
        "pokemon": doc["showdown_id"],
        "name": doc["name"],
        "import_id": imp,
        "total": len(items),
        "items": items,
    }


@router.get("/{id}/moves")
async def get_pokemon_moves(id: str):
    """The Pokemon's learnset resolved against ``sd_moves``.

    Single ``$in`` lookup (no N+1). Each item carries the canonical
    ``learn_sources`` codes (e.g. ``9M``, ``9L14``) from the learnset.
    Formes without their own learnset entry return an empty list — no
    base-species fallback is fabricated.
    """
    imp, doc = await _find_pokemon(id, projection={"showdown_id": 1, "name": 1})
    ls = await get_db()["sd_learnsets"].find_one(
        {"import_id": imp, "showdown_id": doc["showdown_id"]},
        {"_id": 0, "moves": 1},
    )
    moves_map: dict = (ls or {}).get("moves", {})
    move_ids = list(moves_map.keys())
    items: list[dict] = []
    if move_ids:
        items = await get_db()["sd_moves"].find(
            {"import_id": imp, "showdown_id": {"$in": move_ids}},
            {"_id": 0, "import_id": 0},
        ).sort("name", 1).to_list(len(move_ids))
        for m in items:
            m["learn_sources"] = moves_map.get(m["showdown_id"], [])
    unresolved = sorted(set(move_ids) - {m["showdown_id"] for m in items})
    return {
        "pokemon": doc["showdown_id"],
        "name": doc["name"],
        "import_id": imp,
        "total": len(items),
        "items": items,
        "unresolved": unresolved,
    }
