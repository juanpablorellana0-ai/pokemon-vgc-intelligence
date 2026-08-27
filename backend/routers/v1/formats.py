from fastapi import APIRouter, Query
from db import get_db
from ._query import paged_list

router = APIRouter(prefix="/formats", tags=["formats"])


@router.get("")
async def list_formats(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    section: str | None = None,
    vgc: bool | None = None,
    champions: bool | None = None,
    doubles: bool | None = None,
    mod: str | None = None,
):
    filt: dict = {}
    if section:
        filt["section"] = section
    if vgc is not None:
        filt["is_vgc"] = vgc
    if champions is not None:
        filt["is_champions"] = champions
    if doubles is not None:
        filt["is_doubles"] = doubles
    if mod:
        filt["mod"] = mod
    return await paged_list(
        get_db(), "sd_formats",
        limit=limit, offset=offset,
        extra_filter=filt, sort=[("section", 1), ("name", 1)],
    )
