from fastapi import APIRouter
from db import get_db
from models import Standing

router = APIRouter(prefix="/standings", tags=["standings"])


@router.get("", response_model=list[Standing])
async def list_standings():
    db = get_db()
    docs = await db.standings.find({}, {"_id": 0}).to_list(1000)
    return [Standing(**d) for d in docs]
