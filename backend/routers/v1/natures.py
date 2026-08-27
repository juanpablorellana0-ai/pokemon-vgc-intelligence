from fastapi import APIRouter, Query
from db import get_db
from ._query import paged_list

router = APIRouter(prefix="/natures", tags=["natures"])


@router.get("")
async def list_natures(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await paged_list(
        get_db(), "sd_natures",
        limit=limit, offset=offset,
        sort=[("name", 1)],
    )
