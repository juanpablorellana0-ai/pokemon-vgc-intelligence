"""Claude (Anthropic) integration via the Emergent universal key.

Two public surfaces:
- ``ClaudeService.stream_chat`` — multi-turn VGC coaching chat (SSE).
- ``ClaudeService.analyze_team`` — one-shot team analysis (non-streaming).

Sessions are kept in an in-process dict so multi-turn history survives
across HTTP requests inside a single backend process. A production
deployment will swap this for a Mongo-backed store; this is fine for the
foundation phase.
"""
from __future__ import annotations
import os
from typing import AsyncIterator, Optional

from emergentintegrations.llm.chat import (
    LlmChat,
    UserMessage,
    TextDelta,
    StreamDone,
)

MODEL_PROVIDER = "anthropic"
MODEL_NAME = "claude-sonnet-5"

VGC_COACH_SYSTEM_PROMPT = (
    "You are VGC Coach, an expert coach for Pokémon VGC (Video Game "
    "Championships) and Pokémon Champions. You know the current format, "
    "restricted / legendary rules, common archetypes, speed control, "
    "redirection, weather, terrain, Tera type strategy, and the metagame "
    "of the most recent Regulation. "
    "Give concise, actionable advice. When the user shares a team, point "
    "out concrete weaknesses, missing coverage, and realistic threats. "
    "Never invent tournament placements or usage percentages you can't "
    "cite. If the user asks for exact damage numbers, tell them to use "
    "the deterministic Damage Calculator (do not guess damage). "
    "Reply in the language the user writes in (English or Spanish)."
)

TEAM_ANALYSIS_SYSTEM_PROMPT = (
    "You are a VGC team analyst. You receive a structured JSON team and "
    "return a compact textual report with: (1) archetype label, "
    "(2) win conditions, (3) weak matchups, (4) suggested tech options. "
    "Do NOT compute damage. Do NOT fabricate statistics. Keep the tone "
    "professional and terse — this is expert-facing output."
)


class ClaudeService:
    """Thin wrapper around ``LlmChat`` scoped to Claude Sonnet 5."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self._api_key = api_key or os.environ.get("EMERGENT_LLM_KEY")
        if not self._api_key:
            raise RuntimeError(
                "EMERGENT_LLM_KEY is not set. Add it to backend/.env."
            )
        # session_id -> LlmChat instance. In-process only.
        self._sessions: dict[str, LlmChat] = {}

    # -- Coach chat (multi-turn, streaming) --------------------------------
    def _get_or_create(self, session_id: str) -> LlmChat:
        chat = self._sessions.get(session_id)
        if chat is None:
            chat = LlmChat(
                api_key=self._api_key,
                session_id=session_id,
                system_message=VGC_COACH_SYSTEM_PROMPT,
            ).with_model(MODEL_PROVIDER, MODEL_NAME)
            self._sessions[session_id] = chat
        return chat

    async def stream_chat(
        self, session_id: str, message: str
    ) -> AsyncIterator[str]:
        chat = self._get_or_create(session_id)
        async for event in chat.stream_message(UserMessage(text=message)):
            if isinstance(event, TextDelta):
                yield event.content
            elif isinstance(event, StreamDone):
                return

    def reset_session(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    # -- Team analysis (one-shot, non-streaming) ---------------------------
    async def analyze_team(self, team_payload: dict) -> str:
        chat = LlmChat(
            api_key=self._api_key,
            session_id=f"analysis-{team_payload.get('name', 'anon')}",
            system_message=TEAM_ANALYSIS_SYSTEM_PROMPT,
        ).with_model(MODEL_PROVIDER, MODEL_NAME)

        import json as _json
        prompt = (
            "Analyze this VGC team JSON and reply with the report described "
            "in your system message.\n\n"
            f"{_json.dumps(team_payload, ensure_ascii=False, indent=2)}"
        )
        return await chat.send_message(UserMessage(text=prompt))
