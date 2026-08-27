from fastapi import APIRouter, Query
from db import get_db
from ._query import paged_list

router = APIRouter(prefix="/moves", tags=["moves"])


@router.get("")
async def list_moves(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    type: str | None = None,
    category: str | None = None,
    q: str | None = None,
):
    filt: dict = {}
    if type:
        filt["type"] = type
    if category:
        filt["category"] = category
    if q:
        filt["name"] = {"$regex": q, "$options": "i"}
    return await paged_list(
        get_db(), "sd_moves",
        limit=limit, offset=offset,
        extra_filter=filt, sort=[("name", 1)],
    )
