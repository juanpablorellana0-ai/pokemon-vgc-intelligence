"""Minimal stub of emergentintegrations.llm.chat.

The real package is Emergent-platform-specific and not on PyPI.
This stub provides the interface surface used by ai_services.claude_service
so the backend imports cleanly. AI endpoints still require EMERGENT_LLM_KEY
and will raise RuntimeError (→ HTTP 503) when called without one.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, AsyncIterator


@dataclass
class UserMessage:
    text: str = ""
    images: list = field(default_factory=list)


@dataclass
class TextDelta:
    content: str = ""


@dataclass
class StreamDone:
    pass


class LlmChat:
    def __init__(
        self,
        api_key: str,
        session_id: str,
        system_message: str = "",
        **kwargs: Any,
    ) -> None:
        self.api_key = api_key
        self.session_id = session_id
        self.system_message = system_message
        self._provider: str | None = None
        self._model: str | None = None

    def with_model(self, provider: str, model: str) -> "LlmChat":
        self._provider = provider
        self._model = model
        return self

    async def stream_message(self, message: UserMessage) -> AsyncIterator[Any]:
        raise RuntimeError(
            "emergentintegrations stub — real LLM backend not available"
        )

    async def send_message(self, message: UserMessage) -> str:
        raise RuntimeError(
            "emergentintegrations stub — real LLM backend not available"
        )
