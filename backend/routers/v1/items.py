from fastapi import APIRouter
from db import get_db
from models import Item

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[Item])
async def list_items():
    db = get_db()
    docs = await db.items.find({}, {"_id": 0}).to_list(1000)
    return [Item(**d) for d in docs]
