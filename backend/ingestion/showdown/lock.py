"""Mongo-backed advisory lock — ensures two syncs never run at once.

Uses a single document with ``_id="showdown_sync_lock"``. Acquiring the
lock is an atomic ``insert_one``; releasing is ``delete_one``. A stale
lock older than ``LOCK_TTL_SECONDS`` is considered abandoned and can be
force-broken.
"""
from __future__ import annotations
from datetime import datetime, timezone, timedelta
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

LOCK_ID = "showdown_sync_lock"
LOCK_TTL_SECONDS = 1800  # 30 minutes


async def acquire(db: AsyncIOMotorDatabase, owner: str) -> bool:
    now = datetime.now(timezone.utc)

    # Break stale locks first.
    await db.locks.delete_one({
        "_id": LOCK_ID,
        "acquiredAt": {"$lt": now - timedelta(seconds=LOCK_TTL_SECONDS)},
    })

    try:
        await db.locks.insert_one({
            "_id": LOCK_ID,
            "owner": owner,
            "acquiredAt": now,
        })
        return True
    except Exception:
        return False


async def release(db: AsyncIOMotorDatabase, owner: Optional[str] = None) -> bool:
    q: dict = {"_id": LOCK_ID}
    if owner is not None:
        q["owner"] = owner
    result = await db.locks.delete_one(q)
    return result.deleted_count > 0


async def is_locked(db: AsyncIOMotorDatabase) -> bool:
    doc = await db.locks.find_one({"_id": LOCK_ID}, {"_id": 0})
    return doc is not None
