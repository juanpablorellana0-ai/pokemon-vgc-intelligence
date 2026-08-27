# PRD — VGC Intelligence (Foundation Phase)

## Purpose
Ship the foundational architecture for a production-quality competitive Pokémon VGC analytics / team-building / tournament-prep / coaching platform. This phase delivers only the skeleton — no fabricated statistics, no live integrations.

## Scope (delivered)
- Expo (mobile + web) frontend with bilingual UI (ES / EN), dark esports theme.
- 4-tab bottom navigation: **Home, Meta, Tournaments, Menu**.
- Menu screen exposes: Teams, Team Builder, Damage Calculator, Analyzer, VGC Guide.
- FastAPI backend under `/api/v1/*` with empty resource endpoints:
  `/pokemon`, `/moves`, `/items`, `/abilities`, `/teams`, `/tournaments`, `/standings`, `/meta/usage`, `/cores`, `/sources`, `/health`.
- MongoDB models: `Pokemon`, `PokemonForm`, `Move`, `Ability`, `Item`, `Nature`, `Team`, `TeamPokemon`, `Tournament`, `Player`, `Standing`, `UsageStat`, `Core`, `DataSource`.
- Source-adapter registry with 8 placeholders: Pikalytics, MunchStats, Replica Teams, LabMaus, ReportWorm, Cut Explorer, Showdown, VGC Guide.
- Reserved namespaces for deterministic `calculation` engine and `ai_services` (kept separate).
- **Claude Sonnet 5 integration** (via Emergent LLM key) in `backend/ai_services`:
  - `POST /api/v1/ai/coach/chat` — SSE streaming multi-turn VGC coaching chat.
  - `DELETE /api/v1/ai/coach/chat/{session_id}` — session reset.
  - `POST /api/v1/ai/analyze/team` — one-shot team analysis.
- **Pokémon Showdown sync infrastructure** in `backend/ingestion/showdown` (no data import yet):
  - `ShowdownSyncService` — full versioned pipeline (check → fetch → validate → tests → activate).
  - Mongo advisory lock (`showdown_sync_lock`) — concurrent syncs impossible.
  - Rollback to previous known-good dataset.
  - Structured logs (`SHOWDOWN_SYNC_STARTED`, `SHOWDOWN_VALIDATION_FAILED`, …).
  - Admin API protected by `X-Admin-Token`: `/admin/showdown/{status,check,sync,rollback}`.
  - `documentation/DATA_SOURCES.md` with MIT attribution + architecture.
- Documentation: `README.md`, `documentation/ROADMAP.md`, `documentation/DATA_SOURCES.md`.
- Tests: backend health, DB connection, API surface, Showdown sync + admin protection (25 tests total).

## Out of scope (deferred)
- Real data / ingestion.
- Damage calculator math.
- Authentication.
- Deployment lock-down (CORS, rate limits).

## Constraints
- No fabricated competitive stats anywhere.
- Damage engine must remain deterministic and independent from AI services.
- No hardcoded env values.
- API routes must be prefixed with `/api`.
