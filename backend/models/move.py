from __future__ import annotations
from typing import Optional
from ._base import VGCBase


class Move(VGCBase):
    name: str
    slug: str
    type: Optional[str] = None
    category: Optional[str] = None  # "physical" | "special" | "status"
    base_power: Optional[int] = None
    accuracy: Optional[int] = None
    priority: int = 0
