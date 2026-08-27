from __future__ import annotations
from typing import Optional
from pydantic import Field
from ._base import VGCBase


class Pokemon(VGCBase):
    """A canonical Pokemon species entry.

    Base stats and typing are intentionally omitted from this initial
    foundation. They will be populated by the ingestion layer via
    DataSource adapters (e.g. Showdown) in a later phase.
    """
    dex_number: int
    name: str
    slug: str
    generation: Optional[int] = None
    is_legendary: bool = False
    is_mythical: bool = False
    is_restricted: bool = False  # VGC Series-specific flag


class PokemonForm(VGCBase):
    """A specific form of a Pokemon (e.g. Urshifu-Rapid-Strike, Calyrex-Ice)."""
    pokemon_id: str  # FK -> Pokemon.id
    form_name: str
    slug: str
    is_default: bool = False
