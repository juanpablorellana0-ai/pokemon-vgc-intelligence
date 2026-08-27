from fastapi import APIRouter
from db import get_db
from models import Tournament

router = APIRouter(prefix="/tournaments", tags=["tournaments"])


@router.get("", response_model=list[Tournament])
async def list_tournaments():
    db = get_db()
    docs = await db.tournaments.find({}, {"_id": 0}).to_list(1000)
    return [Tournament(**d) for d in docs]
