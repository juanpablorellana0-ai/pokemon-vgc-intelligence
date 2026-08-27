from fastapi import APIRouter, Query
from db import get_db
from ._query import paged_list

router = APIRouter(prefix="/rulesets", tags=["rulesets"])


@router.get("")
async def list_rulesets(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    q: str | None = None,
):
    filt: dict = {}
    if q:
        filt["name"] = {"$regex": q, "$options": "i"}
    return await paged_list(
        get_db(), "sd_rulesets",
        limit=limit, offset=offset,
        extra_filter=filt, sort=[("name", 1)],
    )
