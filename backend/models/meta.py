from __future__ import annotations
from typing import Optional
from ._base import VGCBase


class UsageStat(VGCBase):
    """A single usage datapoint scoped to (format, snapshot, pokemon_form).

    All numeric fields are Optional so that empty/development rows are
    valid. No fabricated statistics ship in this phase.
    """
    format: str
    snapshot: str  # e.g. "2025-09" or a source-provided cursor
    pokemon_form_id: Optional[str] = None
    usage_percent: Optional[float] = None
    rank: Optional[int] = None
    source_id: Optional[str] = None  # FK -> DataSource.id


class Core(VGCBase):
    """A recurring co-usage cluster (typically 2-3 Pokemon)."""
    format: str
    snapshot: str
    member_pokemon_form_ids: list[str] = []
    frequency: Optional[float] = None
    source_id: Optional[str] = None
