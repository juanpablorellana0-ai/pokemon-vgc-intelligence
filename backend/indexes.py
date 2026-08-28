"""Idempotent Mongo index creation for the Showdown data collections.

Called once at API startup. ``create_index`` is a no-op when the index
already exists, so this is safe to run on every boot and after every
new Showdown import (documents are scoped by ``import_id``, which leads
every compound index).
"""
from __future__ import annotations
import logging

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

INDEXES: dict[str, list[list[tuple[str, int]]]] = {
    "sd_pokemon": [
        [("import_id", 1), ("showdown_id", 1)],
        [("import_id", 1), ("num", 1)],
        [("import_id", 1), ("types", 1)],
        [("import_id", 1), ("is_base", 1)],
        [("import_id", 1), ("name", 1)],
    ],
    "sd_learnsets": [[("import_id", 1), ("showdown_id", 1)]],
    "sd_moves": [
        [("import_id", 1), ("showdown_id", 1)],
        [("import_id", 1), ("name", 1)],
    ],
    "sd_abilities": [[("import_id", 1), ("showdown_id", 1)]],
    "sd_items": [[("import_id", 1), ("showdown_id", 1)]],
    "sd_natures": [[("import_id", 1), ("showdown_id", 1)]],
    "sd_types": [[("import_id", 1), ("showdown_id", 1)]],
    "sd_formats": [[("import_id", 1), ("showdown_id", 1)]],
}


async def ensure_indexes(db: AsyncIOMotorDatabase) -> None:
    created = 0
    for coll, specs in INDEXES.items():
        for spec in specs:
            await db[coll].create_index(spec)
            created += 1
    logger.info("ensure_indexes: %d indexes ensured", created)
