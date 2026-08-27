from __future__ import annotations
from typing import Optional
from ._base import VGCBase


class Item(VGCBase):
    name: str
    slug: str
    category: Optional[str] = None  # "berry" | "held" | "mega-stone" | ...
    description: Optional[str] = None
