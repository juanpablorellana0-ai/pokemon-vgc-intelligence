"""Ingestion layer. Owns all external data-source adapters.

Nothing in this layer performs network I/O in the foundation phase.
The adapters expose a common interface so future phases can add
scheduled ingestion jobs without touching the API layer.
"""
