from __future__ import annotations
from typing import Optional, Dict
from ._base import VGCBase


class TeamPokemon(VGCBase):
    """A single slot on a Team. EVs / IVs / moves are placeholders."""
    team_id: str  # FK -> Team.id
    slot: int  # 1..6
    pokemon_form_id: Optional[str] = None  # FK -> PokemonForm.id
    ability_id: Optional[str] = None
    item_id: Optional[str] = None
    nature_id: Optional[str] = None
    tera_type: Optional[str] = None
    move_ids: list[str] = []
    evs: Dict[str, int] = {}  # {"hp":0,"atk":0,...}
    ivs: Dict[str, int] = {}


class Team(VGCBase):
    name: str
    format: Optional[str] = None  # e.g. "VGC 2025 Reg G"
    author: Optional[str] = None
    notes: Optional[str] = None
    source_id: Optional[str] = None  # FK -> DataSource.id (if imported)
