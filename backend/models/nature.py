from __future__ import annotations
from typing import Optional
from ._base import VGCBase


class Nature(VGCBase):
    name: str  # e.g. "Adamant"
    increased_stat: Optional[str] = None  # e.g. "attack"
    decreased_stat: Optional[str] = None  # e.g. "spa"
