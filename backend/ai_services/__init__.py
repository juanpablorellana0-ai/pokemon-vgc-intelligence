"""AI services layer.

Home for LLM-backed features (VGC coaching chat, team analysis, ...).
This module MUST stay independent from ``backend.calculation`` — the
damage engine remains deterministic.
"""
from .claude_service import ClaudeService, VGC_COACH_SYSTEM_PROMPT, TEAM_ANALYSIS_SYSTEM_PROMPT

__all__ = [
    "ClaudeService",
    "VGC_COACH_SYSTEM_PROMPT",
    "TEAM_ANALYSIS_SYSTEM_PROMPT",
]
