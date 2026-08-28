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

## Governance (Jun 2026)
- Created root `/app/AGENTS.md`: permanent rules for AI agents. Branch architecture (main=protected source of truth, emergent/development=only writable branch for agents, frontend/paola=designer-owned untouchable), GitHub workflow (sync with main before major work, no force-push/deletes/resets, PRs to main never self-merged), designer-sensitive frontend areas, backend/frontend separation, code/data safety, testing & PR requirements, conflict behavior (safety first, stop and ask). Documentation-only — no code changes.

## Phase 3A — Pokémon Data Explorer (Jun 2026) — DONE
- Backend (reused existing router/conventions, no duplicates):
  - `GET /api/v1/pokemon`: pagination envelope extended with `page`/`pages` (in shared `_query.paged_list`, applies to all list endpoints); filters: `q` (regex-escaped ci substring), `type` (ci exact), `ability` (ci exact over slots 0/1/H/S), `only_base`, `include_special` (default false → hides num<=0 CAP/Pokestar/MissingNo).
  - `GET /api/v1/pokemon/{id}`: toID() normalization, base-species preference on dex-number lookups, learnset attached.
  - NEW `GET /api/v1/pokemon/{id}/abilities` + `/{id}/moves` (single $in resolution, learn_sources included, `unresolved` reported).
  - NEW `backend/indexes.py`: idempotent compound indexes (import_id-led) created at startup via server.py startup event.
- Frontend placeholder (existing theme/i18n, designer can redesign):
  - `/pokemon` list: debounced search, type chips (from /types), only-base chip, prev/next server pagination, loading/error/empty states.
  - `/pokemon/[id]` detail: identity, stat bars, abilities (hidden badge), moves list, loading/error/404 states.
  - `src/api/client.ts` typed fetch client (EXPO_PUBLIC_BACKEND_URL). Home tile (LIVE badge) + Menu row entries.
- Tests: tests/test_pokemon_explorer.py (20 tests) → 54/54 pytest passing. Testing agent frontend E2E: 18/18 pass (iteration_2.json).
- Docs: documentation/API.md (new), ROADMAP Phase 1 items checked.
- Known canonical-data gaps (documented, not invented): no generation field, no per-Pokémon format legality, null desc/short_desc on moves/abilities, no base-species learnset fallback for formes.
