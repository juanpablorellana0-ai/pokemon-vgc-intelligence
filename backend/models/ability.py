from __future__ import annotations
from typing import Optional
from ._base import VGCBase


class Ability(VGCBase):
    name: str
    slug: str
    description: Optional[str] = None
