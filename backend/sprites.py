"""Pokemon sprite URL resolver (Roadmap Phase 1: URL builder — no scraping).

Builds stable image references against Pokemon Showdown's public sprite
CDN. Nothing is downloaded or stored; URLs are computed at read time from
the canonical document, so no data is duplicated in Mongo.

Sprite id rule (mirrors Showdown's own spriteid):
    base species toID + '-' + forme toID   (e.g. ``venusaur-mega``)
    plain species toID otherwise           (e.g. ``gholdengo``)

The ``gen5`` set is used because it is the only complete static set that
covers every species and forme (Showdown commissions BW-style sprites
for all new generations). ``image_fallback_url`` points to Showdown's
generic unknown-Pokemon sprite; the frontend swaps to it on load error.
"""
from __future__ import annotations
import re

SPRITE_BASE = "https://play.pokemonshowdown.com/sprites"
FALLBACK_SPRITE_URL = f"{SPRITE_BASE}/gen5/0.png"


def _to_id(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def sprite_id(doc: dict) -> str:
    """Showdown sprite id for a canonical ``sd_pokemon`` document."""
    base = doc.get("base_species_name")
    forme = doc.get("forme")
    if base and forme:
        return f"{_to_id(base)}-{_to_id(forme)}"
    return doc.get("showdown_id") or _to_id(doc.get("name", ""))


def attach_image_urls(doc: dict) -> dict:
    """Add ``image_url`` / ``image_fallback_url`` to an API response doc."""
    doc["image_url"] = f"{SPRITE_BASE}/gen5/{sprite_id(doc)}.png"
    doc["image_fallback_url"] = FALLBACK_SPRITE_URL
    return doc
