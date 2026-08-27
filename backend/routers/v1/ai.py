"""AI-backed endpoints (Claude Sonnet 5 via Emergent LLM key).

These routes live under ``/api/v1/ai/*`` and never touch the
deterministic calculation module.
"""
from __future__ import annotations
from typing import Optional, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ai_services import ClaudeService

router = APIRouter(prefix="/ai", tags=["ai"])

# Single service instance — LlmChat is created per session inside it.
_service: Optional[ClaudeService] = None


def _svc() -> ClaudeService:
    global _service
    if _service is None:
        try:
            _service = ClaudeService()
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    return _service


# -- Coach chat ------------------------------------------------------------
class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=4000)


@router.post("/coach/chat")
async def coach_chat(req: ChatRequest):
    """Server-Sent Events stream of Claude's reply.

    The client keeps a stable ``session_id`` (UUID recommended) to preserve
    multi-turn history within a single backend process.
    """
    svc = _svc()

    async def event_gen():
        try:
            async for delta in svc.stream_chat(req.session_id, req.message):
                # SSE frame — one delta per event
                yield f"data: {delta}\n\n"
            yield "event: done\ndata: [DONE]\n\n"
        except Exception as exc:  # pragma: no cover - upstream error
            yield f"event: error\ndata: {str(exc)}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@router.delete("/coach/chat/{session_id}")
async def reset_chat(session_id: str):
    removed = _svc().reset_session(session_id)
    return {"reset": removed}


# -- Team analysis ---------------------------------------------------------
class TeamAnalysisRequest(BaseModel):
    """Loose schema on purpose — team shape will evolve with Team model."""
    name: Optional[str] = None
    format: Optional[str] = None
    pokemon: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of {species, ability, item, tera_type, moves, evs, nature}",
    )


class TeamAnalysisResponse(BaseModel):
    model: str
    analysis: str


@router.post("/analyze/team", response_model=TeamAnalysisResponse)
async def analyze_team(req: TeamAnalysisRequest):
    if not req.pokemon:
        raise HTTPException(status_code=400, detail="team.pokemon is empty")
    text = await _svc().analyze_team(req.model_dump())
    return TeamAnalysisResponse(model="claude-sonnet-5", analysis=text)
