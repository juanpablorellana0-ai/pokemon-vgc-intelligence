from fastapi import APIRouter
from db import get_db
from models import UsageStat

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/usage", response_model=list[UsageStat])
async def list_usage():
    db = get_db()
    docs = await db.usage_stats.find({}, {"_id": 0}).to_list(1000)
    return [UsageStat(**d) for d in docs]
