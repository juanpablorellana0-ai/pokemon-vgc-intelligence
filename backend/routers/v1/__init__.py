from fastapi import APIRouter
from . import (
    health,
    pokemon,
    moves,
    items,
    abilities,
    teams,
    tournaments,
    standings,
    meta,
    cores,
    sources,
    ai,
    admin,
    natures,
    types,
    formats,
    rulesets,
    regulations,
)

router = APIRouter(prefix="/v1")
router.include_router(health.router)
router.include_router(pokemon.router)
router.include_router(moves.router)
router.include_router(items.router)
router.include_router(abilities.router)
router.include_router(natures.router)
router.include_router(types.router)
router.include_router(formats.router)
router.include_router(rulesets.router)
router.include_router(regulations.router)
router.include_router(teams.router)
router.include_router(tournaments.router)
router.include_router(standings.router)
router.include_router(meta.router)
router.include_router(cores.router)
router.include_router(sources.router)
router.include_router(ai.router)
router.include_router(admin.router)
