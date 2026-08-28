"""Shared helpers for v1 data-read endpoints.

Reads Showdown data from Mongo scoped to the currently active
``import_id`` recorded in the pointer document.
"""
from __future__ import annotations
from typing import Optional
from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase


async def active_import_id(db: AsyncIOMotorDatabase) -> Optional[str]:
    doc = await db["showdown_pointers"].find_one(
        {"_id": "showdown_active_dataset"},
        {"_id": 0, "activeImportId": 1},
    )
    return (doc or {}).get("activeImportId")


async def require_active_import(db: AsyncIOMotorDatabase) -> str:
    imp = await active_import_id(db)
    if not imp:
        raise HTTPException(
            status_code=503,
            detail="no active Showdown dataset — run /admin/showdown/sync first",
        )
    return imp


async def paged_list(
    db: AsyncIOMotorDatabase,
    collection: str,
    *,
    limit: int,
    offset: int,
    extra_filter: dict | None = None,
    projection: dict | None = None,
    sort: list[tuple[str, int]] | None = None,
) -> dict:
    imp = await require_active_import(db)
    limit = max(1, min(500, limit))
    offset = max(0, offset)
    proj = {"_id": 0, "import_id": 0}
    if projection:
        proj.update(projection)
    q = {"import_id": imp}
    if extra_filter:
        q.update(extra_filter)
    total = await db[collection].count_documents(q)
    cursor = db[collection].find(q, proj).skip(offset).limit(limit)
    if sort:
        cursor = cursor.sort(sort)
    items = await cursor.to_list(limit)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "page": (offset // limit) + 1,
        "pages": (total + limit - 1) // limit if total else 0,
        "import_id": imp,
        "items": items,
    }
