from fastapi import APIRouter
from db import get_db
from models import Team

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[Team])
async def list_teams():
    db = get_db()
    docs = await db.teams.find({}, {"_id": 0}).to_list(1000)
    return [Team(**d) for d in docs]
