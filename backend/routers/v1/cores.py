from fastapi import APIRouter
from db import get_db
from models import Core

router = APIRouter(prefix="/cores", tags=["cores"])


@router.get("", response_model=list[Core])
async def list_cores():
    db = get_db()
    docs = await db.cores.find({}, {"_id": 0}).to_list(1000)
    return [Core(**d) for d in docs]
