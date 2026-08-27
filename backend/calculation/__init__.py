"""Deterministic VGC calculation engine.

Reserved for the future damage calculator. This module MUST NOT depend on
any AI service. Implementations will be pure functions over typed inputs
so results are reproducible and unit-testable.
"""
from .engine import DamageEngine

__all__ = ["DamageEngine"]
