from fastapi import APIRouter, Query
from db import get_db
from ._query import paged_list

router = APIRouter(prefix="/items", tags=["items"])


@router.get("")
async def list_items(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    q: str | None = None,
):
    filt: dict = {}
    if q:
        filt["name"] = {"$regex": q, "$options": "i"}
    return await paged_list(
        get_db(), "sd_items",
        limit=limit, offset=offset,
        extra_filter=filt, sort=[("name", 1)],
    )
