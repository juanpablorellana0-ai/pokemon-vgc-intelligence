"""Placeholder for the deterministic damage engine.

Design constraints (enforced in future phases):
- Pure functions, no I/O, no randomness at the boundary.
- All inputs typed; no strings-as-magic-values.
- No AI/LLM calls anywhere in this module.
"""
from __future__ import annotations


class DamageEngine:
    """Reserved namespace. No calculations implemented yet."""

    version: str = "0.0.0-foundation"

    def calculate(self, *args, **kwargs):  # noqa: D401
        raise NotImplementedError(
            "Damage engine not implemented in the foundation phase."
        )
