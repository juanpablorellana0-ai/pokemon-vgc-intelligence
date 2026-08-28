"""VGC Intelligence backend entry point.

Only responsibilities of this module:
- create the FastAPI app
- wire CORS
- mount the versioned API router (/api/v1/*)
- expose a top-level /api ping for legacy checks
- close the Mongo client on shutdown

Domain logic lives in ``models``, ``routers``, ``ingestion``,
``calculation``, and ``ai_services``.
"""
from __future__ import annotations
import logging
import sys
from pathlib import Path

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")
# Make sibling packages (models, routers, ingestion, ...) importable when
# uvicorn is started with a different CWD.
sys.path.insert(0, str(ROOT_DIR))

from db import close_client, get_db  # noqa: E402
from indexes import ensure_indexes  # noqa: E402
from routers.v1 import router as v1_router  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="VGC Intelligence API", version="0.1.0")

api_router = APIRouter(prefix="/api")


@api_router.get("")
async def api_root():
    return {
        "service": "vgc-intelligence-api",
        "status": "ok",
        "docs": "/docs",
        "versions": ["v1"],
    }


api_router.include_router(v1_router)
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup() -> None:
    await ensure_indexes(get_db())


@app.on_event("shutdown")
async def _shutdown() -> None:
    await close_client()
