from fastapi import APIRouter, Query
from db import get_db
from ._query import paged_list, require_active_import

router = APIRouter(prefix="/types", tags=["types"])


@router.get("")
async def list_types(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    return await paged_list(
        get_db(), "sd_types",
        limit=limit, offset=offset,
        sort=[("name", 1)],
    )


@router.get("/chart")
async def type_chart():
    """Full type effectiveness chart. One entry per type."""
    imp = await require_active_import(get_db())
    docs = await get_db()["sd_typechart"].find(
        {"import_id": imp}, {"_id": 0, "import_id": 0},
    ).to_list(50)
    return {"import_id": imp, "items": docs}
