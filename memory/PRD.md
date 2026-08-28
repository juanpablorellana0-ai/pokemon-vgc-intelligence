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
- **Pokémon Showdown data pipeline** in `backend/ingestion/showdown` (Phase 2B — canonical import):
  - `ShowdownSyncService` — versioned pipeline (check → clone → parse → normalize → validate → tests → activate).
  - Node parser (`parser/parse.mjs`) using esbuild to transpile Showdown's TS data files.
  - Python normalizers for pokemon/forms/moves/abilities/items/natures/types/typechart/learnsets/formats/rulesets + Champions overlay.
  - RAW snapshot preserved on disk **and** in `sd_raw` collection.
  - Mongo advisory lock (`showdown_sync_lock`) — concurrent syncs impossible.
  - Rollback to previous known-good dataset via pointer.
  - Structured logs for every phase.
  - Admin API protected by `X-Admin-Token`: `/admin/showdown/{status,check,sync,rollback}`.
  - Public read API: `/pokemon(/id)`, `/moves`, `/abilities`, `/items`, `/natures`, `/types(/chart)`, `/formats`, `/rulesets`, `/regulations` — all paginated, all filter by active `import_id`.
  - Initial canonical import active at commit `5e8ead64b366aa55b83be979dd3d1050115e8bfe`.
- Documentation: `README.md`, `documentation/ROADMAP.md`, `documentation/DATA_SOURCES.md`.
- Tests: 34 total (foundation health, API surface, showdown sync stubs, live imported data).

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

## Documentation for designer (Jun 2026)
- Created `frontend/FRONTEND_GUIDE.md` (Spanish): onboarding guide for Paola (designer). Covers product overview/vision, 13 product areas with real status, responsibilities, frontend architecture (Expo Router, theme tokens, i18n, components), API boundary with endpoint list (real vs empty), assets, git workflow (main / frontend/paola / emergent/development), design roadmap (Phases A–F), placeholder philosophy, dev rules (testIDs, i18n, protected files). Documentation-only task — no code/behavior changes.
