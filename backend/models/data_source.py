from __future__ import annotations
from typing import Optional
from ._base import VGCBase


class DataSource(VGCBase):
    """Registry entry describing an external data provider.

    The row is created once per external site (Pikalytics, MunchStats, ...)
    and referenced by ingested records for provenance. No adapter fetches
    live data in this foundation phase.
    """
    key: str  # unique slug, e.g. "pikalytics"
    name: str
    homepage: Optional[str] = None
    enabled: bool = False
    notes: Optional[str] = None
