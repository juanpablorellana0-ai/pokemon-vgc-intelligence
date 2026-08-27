"""Pokémon Showdown synchronization infrastructure.

This subpackage owns everything required to safely track and version the
upstream ``smogon/pokemon-showdown`` repository. It does NOT import the
dataset in this phase — only the sync pipeline, versioning, locking,
history and rollback machinery.
"""
from .service import ShowdownSyncService
from .models import ShowdownSyncHistory, SyncStatus

__all__ = ["ShowdownSyncService", "ShowdownSyncHistory", "SyncStatus"]
