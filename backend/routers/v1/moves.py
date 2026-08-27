from fastapi import APIRouter
from db import get_db
from models import Move

router = APIRouter(prefix="/moves", tags=["moves"])


@router.get("", response_model=list[Move])
async def list_moves():
    db = get_db()
    docs = await db.moves.find({}, {"_id": 0}).to_list(1000)
    return [Move(**d) for d in docs]
