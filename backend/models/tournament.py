from __future__ import annotations
from typing import Optional
from datetime import date
from ._base import VGCBase


class Tournament(VGCBase):
    name: str
    slug: str
    format: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    location: Optional[str] = None
    source_id: Optional[str] = None  # FK -> DataSource.id


class Player(VGCBase):
    handle: str
    country: Optional[str] = None


class Standing(VGCBase):
    tournament_id: str  # FK -> Tournament.id
    player_id: str  # FK -> Player.id
    placement: Optional[int] = None
    team_id: Optional[str] = None  # FK -> Team.id
    wins: Optional[int] = None
    losses: Optional[int] = None
