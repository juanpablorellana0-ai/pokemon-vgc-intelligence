"""Read-only foundation endpoints. Return `[]` until ingestion lands."""
from fastapi import APIRouter
from db import get_db
from models import Pokemon

router = APIRouter(prefix="/pokemon", tags=["pokemon"])


@router.get("", response_model=list[Pokemon])
async def list_pokemon():
    db = get_db()
    docs = await db.pokemon.find({}, {"_id": 0}).to_list(1000)
    return [Pokemon(**d) for d in docs]
