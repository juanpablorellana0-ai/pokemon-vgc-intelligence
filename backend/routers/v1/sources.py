"""Introspection endpoint listing all registered data-source adapters."""
from fastapi import APIRouter
from ingestion.adapters import REGISTRY

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("")
async def list_sources():
    return [a.status().__dict__ for a in REGISTRY.values()]
