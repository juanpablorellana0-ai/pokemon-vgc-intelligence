"""VGC Regulation formats — a filtered projection of ``sd_formats``.

Regulations are the successive VGC rulesets used at Play! Pokémon events
(e.g. "Regulation G"). Showdown labels them inside format names like
"[Gen 9] VGC 2025 Reg G"; we surface the subset here for convenience.
"""
import re
from fastapi import APIRouter, Query
from db import get_db
from ._query import paged_list

router = APIRouter(prefix="/regulations", tags=["regulations"])

_REG_RE = re.compile(r"\bReg(?:ulation)?\s+([A-Z])\b", re.IGNORECASE)


@router.get("")
async def list_regulations(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Return VGC formats whose name mentions a Regulation letter."""
    filt = {
        "is_vgc": True,
        "name": {"$regex": r"Reg", "$options": "i"},
    }
    page = await paged_list(
        get_db(), "sd_formats",
        limit=limit, offset=offset,
        extra_filter=filt, sort=[("name", 1)],
    )
    # Extract the regulation letter for each hit
    for item in page["items"]:
        m = _REG_RE.search(item.get("name", ""))
        item["regulation"] = m.group(1).upper() if m else None
    return page
