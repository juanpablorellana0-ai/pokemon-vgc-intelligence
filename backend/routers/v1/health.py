from fastapi import APIRouter
from db import get_db

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health():
    return {"status": "ok", "service": "vgc-intelligence-api", "version": "v1"}


@router.get("/db")
async def health_db():
    db = get_db()
    # ping via a cheap admin command; motor exposes the same api
    result = await db.command("ping")
    return {"status": "ok" if result.get("ok") == 1 else "degraded"}
