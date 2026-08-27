from fastapi import APIRouter
from db import get_db
from models import Ability

router = APIRouter(prefix="/abilities", tags=["abilities"])


@router.get("", response_model=list[Ability])
async def list_abilities():
    db = get_db()
    docs = await db.abilities.find({}, {"_id": 0}).to_list(1000)
    return [Ability(**d) for d in docs]
