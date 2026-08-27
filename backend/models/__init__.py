"""Domain models for VGC Intelligence.

Every model uses UUID string ids (never ObjectId) and is JSON-serializable.
Tables are intentionally empty in this phase. No fabricated competitive stats.
"""
from .pokemon import Pokemon, PokemonForm
from .move import Move
from .ability import Ability
from .item import Item
from .nature import Nature
from .team import Team, TeamPokemon
from .tournament import Tournament, Player, Standing
from .meta import UsageStat, Core
from .data_source import DataSource

__all__ = [
    "Pokemon",
    "PokemonForm",
    "Move",
    "Ability",
    "Item",
    "Nature",
    "Team",
    "TeamPokemon",
    "Tournament",
    "Player",
    "Standing",
    "UsageStat",
    "Core",
    "DataSource",
]
