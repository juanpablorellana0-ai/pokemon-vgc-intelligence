# VGC Intelligence — Development Roadmap

The foundation phase (this repository) ships architecture + placeholders only. Each phase below is scoped so it can be built without rewriting previous work.

---

## Phase 0 — Foundation (this repo)

- [x] Project scaffold (Expo mobile + web, FastAPI, MongoDB).
- [x] Versioned API `/api/v1/*` with empty resources.
- [x] Pydantic domain models (Pokemon, Move, Team, Tournament, UsageStat, ...).
- [x] Source-adapter registry (Pikalytics, MunchStats, Replica Teams, LabMaus, ReportWorm, Cut Explorer, Showdown, VGC Guide) — all stubs.
- [x] Deterministic calculation engine namespace (empty).
- [x] AI services namespace (empty, separate from calculation).
- [x] Bilingual UI (ES / EN) with dark esports theme.
- [x] Coming Soon states for every placeholder section.
- [x] Backend health, DB and API smoke tests.

---

## Phase 1 — Static reference data

Ingest offline-safe, canonical data first so downstream layers can be built without depending on live external sources.

- Species / forms / moves / abilities / items / natures import from a bundled dataset (e.g. Pokémon Showdown reference tables).
- Sprite and artwork resolver (URL builder — no scraping).
- `GET /api/v1/pokemon/{id}` and detail routes.
- Frontend Pokemon browser (searchable list, detail sheet).

---

## Phase 2 — Deterministic damage calculator

- Pure functions in `backend/calculation` implementing VGC-accurate math.
- Inputs typed: attacker, defender, move, field, side conditions.
- Rolls returned as `min..max` arrays (no randomness at the boundary).
- Property-based tests covering STAB, weather, terrain, screens, Tera, spread reduction.
- Frontend Damage Calculator UI wired to `POST /api/v1/calc/damage`.
- **AI is not allowed inside this module.**

---

## Phase 3 — Team model

- Full `Team` + `TeamPokemon` CRUD.
- Showdown paste import/export.
- Team validator (legal moves, abilities, item legality per format).
- Team Builder UI (6 slots, EV spreads, natures, moves).

---

## Phase 4 — Meta ingestion

**Phase 4a — Pokémon Showdown sync infrastructure (delivered)**

- [x] `ShowdownSyncService` with the full pipeline: `check → compare → fetch → validate → tests → activate`.
- [x] Versioned dataset directories (`showdown_dataset_<sha[:12]>`) — active is never overwritten before validation passes.
- [x] Rollback pointer to the previous known-good dataset.
- [x] Mongo advisory lock — two sync jobs can never run at once.
- [x] `showdown_sync_history` collection (id, commits, timings, records, validation errors, test results, activation, error, importer + app version).
- [x] Structured logs for every phase (`SHOWDOWN_SYNC_STARTED`, `SHOWDOWN_UPDATE_AVAILABLE`, ..., `SHOWDOWN_ROLLBACK_COMPLETED`).
- [x] Admin API (`X-Admin-Token`): `GET /admin/showdown/status`, `POST /admin/showdown/check`, `POST /admin/showdown/sync`, `POST /admin/showdown/rollback`.
- [x] Documentation: `documentation/DATA_SOURCES.md` (MIT attribution + architecture).
- [ ] Scheduler (6h default) — infrastructure ready, runner to be wired.
- [ ] Real clone + importer + normalizer (gated behind `SHOWDOWN_ENABLE_CLONE`).

**Phase 4b — Other adapters (planned, not started)**

Each adapter will follow the same isolation contract (own history collection, own dataset dir, own license entry in `DATA_SOURCES.md`):

1. `PikalyticsAdapter` — usage %, top items, top moves per Pokemon.
2. `MunchStatsAdapter` — refined usage + core detection.
3. `ReplicaTeamsAdapter` (champions.karthikb.dev) — Worlds/Regionals team archive.
4. `LabMausAdapter` — advanced meta breakdowns.
5. `ReportWormAdapter` — event coverage.
6. `CutExplorerAdapter` — tournament cut analysis.
7. `ShowdownAdapter` — usage exports + reference tables.
8. `VGCGuideAdapter` — curated educational content.

Every adapter must:
- Cache raw responses.
- Persist results linked to a `DataSource` row for provenance.
- Never leak vendor-specific fields upstream.

---

## Phase 5 — Tournaments

- Tournament model populated from ingestion + manual entry.
- Standings, brackets, cut analysis.
- Player pages.
- Frontend Tournaments browser + tournament detail view.

---

## Phase 6 — Analyzer

- Team coverage matrix.
- Weakness / threat report.
- Speed tiers.
- Common counter-teams from ingested tournament data.

---

## Phase 7 — Coaching (AI services)

- [x] Claude Sonnet 5 wired via Emergent LLM key in `backend/ai_services`.
- [x] `POST /api/v1/ai/coach/chat` — SSE streaming multi-turn chat.
- [x] `POST /api/v1/ai/analyze/team` — one-shot team analysis.
- [ ] Retrieval-augmented Q&A over ingested articles + VGC Guide.
- [ ] Frontend chat UI (deferred — backend-only for now).
- [ ] Persist chat history to Mongo (currently in-process).
- All AI code lives in `backend/ai_services`, never inside `backend/calculation`.

---

## Phase 8 — Accounts & sync

- Authentication (integration via `integration_playbook_expert_v2`).
- Personal team library.
- Cross-device sync.
- CORS lock-down and rate limits.

---

## Non-goals

- Fabricated / made-up competitive statistics at any phase.
- AI-driven damage calculation.
- Scraping providers that forbid it (adapters will use official APIs / permitted feeds).
