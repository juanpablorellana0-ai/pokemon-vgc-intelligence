from fastapi import APIRouter, HTTPException, Query
from db import get_db
from ._query import paged_list, require_active_import

router = APIRouter(prefix="/pokemon", tags=["pokemon"])


@router.get("")
async def list_pokemon(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    only_base: bool = Query(False, description="Only base species (exclude forms)"),
    q: str | None = Query(None, description="Substring on name/slug"),
):
    filt: dict = {}
    if only_base:
        filt["is_base"] = True
    if q:
        filt["$or"] = [
            {"slug": {"$regex": q.lower(), "$options": "i"}},
            {"name": {"$regex": q, "$options": "i"}},
        ]
    return await paged_list(
        get_db(), "sd_pokemon",
        limit=limit, offset=offset,
        extra_filter=filt, sort=[("num", 1), ("name", 1)],
    )


@router.get("/{id}")
async def get_pokemon(id: str):
    imp = await require_active_import(get_db())
    # accept either showdown_id (slug) or numeric num
    q: dict = {"import_id": imp}
    if id.isdigit():
        q["num"] = int(id)
    else:
        q["showdown_id"] = id.lower()
    doc = await get_db()["sd_pokemon"].find_one(q, {"_id": 0, "import_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail=f"pokemon not found: {id}")
    # attach learnset
    ls = await get_db()["sd_learnsets"].find_one(
        {"import_id": imp, "showdown_id": doc["showdown_id"]},
        {"_id": 0, "import_id": 0},
    )
    doc["learnset"] = (ls or {}).get("moves", {})
    return doc
