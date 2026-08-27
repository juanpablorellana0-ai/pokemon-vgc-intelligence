# VGC Intelligence

A **professional-grade competitive Pokémon VGC / Pokémon Champions analytics, team-building, tournament-preparation and coaching platform**.

This repository ships the **foundation** for that platform: a clean, extensible architecture on top of which the analytics, ingestion, calculation and coaching layers will be built in later phases.

> No fabricated competitive statistics ship in this foundation phase. Placeholder screens are clearly marked **Coming Soon**.

---

## Project purpose

VGC Intelligence will unify metagame usage, tournament results, team databases, a deterministic VGC damage calculator, coverage/threat analysis and educational content in a single native + web application.

The foundation focuses on:

- Clean separation between frontend, backend, database, ingestion, calculation and AI services.
- A versioned REST API (`/api/v1/*`).
- A source-adapter architecture ready to plug external data providers.
- A professional esports UI (dark navy/black + blue/purple accents).

---

## Architecture

```
┌────────────────────────┐         ┌──────────────────────────────┐
│  Frontend (Expo/RN)    │◀── HTTP ▶│  Backend API (FastAPI)      │
│  React Native + Web    │         │  /api/v1/*                   │
└────────────────────────┘         └──────────────┬───────────────┘
                                                  │
                       ┌──────────────────────────┼──────────────────────────┐
                       ▼                          ▼                          ▼
             ┌──────────────────┐      ┌─────────────────────┐    ┌───────────────────┐
             │  MongoDB (data)  │      │  Ingestion adapters │    │  Calculation eng. │
             │                  │      │  (Pikalytics, ...)  │    │  (deterministic)  │
             └──────────────────┘      └─────────────────────┘    └───────────────────┘
                                                                            │
                                                                            ▼
                                                                 ┌───────────────────┐
                                                                 │   AI services     │
                                                                 │   (coaching, RAG) │
                                                                 └───────────────────┘
```

Six layers are kept strictly independent:

1. **Frontend** — Expo/React Native app (mobile + web).
2. **Backend API** — FastAPI, versioned under `/api/v1/*`.
3. **Database** — MongoDB (Motor async driver).
4. **Data ingestion** — Source adapters (`backend/ingestion/adapters`).
5. **VGC calculation engine** — Pure, deterministic module (`backend/calculation`). **Must not depend on any AI model.**
6. **AI services** — Reserved namespace (`backend/ai_services`), separate from calculation.

---

## Folder structure

```
/app
├── backend
│   ├── server.py                 # FastAPI entry
│   ├── db.py                     # MongoDB client factory
│   ├── models/                   # Pydantic domain models
│   ├── routers/v1/               # Versioned API routers
│   ├── ingestion/adapters/       # External data-source adapters (stubs)
│   ├── calculation/              # Deterministic damage engine (stub)
│   └── ai_services/              # Reserved for coaching/AI (empty)
├── frontend
│   ├── app/                      # Expo Router routes
│   │   ├── _layout.tsx           # Root layout + providers
│   │   ├── (tabs)/               # Bottom-tabs group (Home, Meta, Tournaments, Menu)
│   │   ├── teams.tsx
│   │   ├── team-builder.tsx
│   │   ├── damage-calculator.tsx
│   │   ├── analyzer.tsx
│   │   └── vgc-guide.tsx
│   └── src/
│       ├── theme.ts              # Design tokens
│       ├── i18n.tsx              # Bilingual (ES/EN) provider
│       └── components/           # ComingSoon, LangToggle, SecondaryScreen
├── documentation
│   └── ROADMAP.md
├── tests
│   ├── test_backend_health.py
│   ├── test_db_connection.py
│   └── test_api_health.py
└── README.md
```

---

## How the backend communicates with the frontend

- The backend exposes everything under **`/api/*`** (Kubernetes ingress rule).
- The frontend reads the base URL from `EXPO_PUBLIC_BACKEND_URL` (in `frontend/.env`) and appends `/api/v1/...` for every request.
- CORS is wide-open in this phase for developer ergonomics; it will be locked down when auth lands.

---

## Database models (foundation)

All models use string UUID ids (never Mongo `ObjectId`) and are JSON-serializable Pydantic classes.

| Model         | Purpose                                     |
|---------------|---------------------------------------------|
| `Pokemon`     | Canonical species entry                     |
| `PokemonForm` | Specific form of a species                  |
| `Move`        | Move definition                             |
| `Ability`     | Ability definition                          |
| `Item`        | Held / consumable item                      |
| `Nature`      | Stat-modifying nature                       |
| `Team`        | Competitive team                            |
| `TeamPokemon` | One of six slots on a team                  |
| `Tournament`  | Tournament metadata                         |
| `Player`      | Competitor identity                         |
| `Standing`    | Player result inside a tournament           |
| `UsageStat`   | Usage datapoint (format + snapshot + form)  |
| `Core`        | Recurring co-usage cluster                  |
| `DataSource`  | External provider registry entry            |

Tables are intentionally empty. No fabricated statistics.

---

## API structure

Base URL: `${EXPO_PUBLIC_BACKEND_URL}/api`

| Endpoint                    | Notes                                     |
|-----------------------------|-------------------------------------------|
| `GET /api`                  | Service info + supported versions         |
| `GET /api/v1/health`        | Liveness                                  |
| `GET /api/v1/health/db`     | Mongo ping                                |
| `GET /api/v1/pokemon`       | Empty list until ingestion lands          |
| `GET /api/v1/moves`         | Empty list                                |
| `GET /api/v1/items`         | Empty list                                |
| `GET /api/v1/abilities`     | Empty list                                |
| `GET /api/v1/teams`         | Empty list                                |
| `GET /api/v1/tournaments`   | Empty list                                |
| `GET /api/v1/standings`     | Empty list                                |
| `GET /api/v1/meta/usage`    | Empty list                                |
| `GET /api/v1/cores`         | Empty list                                |
| `GET /api/v1/sources`       | Adapter registry (all `implemented=false`) |
| `POST /api/v1/ai/coach/chat` | SSE stream — VGC coaching chat (Claude Sonnet 5) |
| `DELETE /api/v1/ai/coach/chat/{session_id}` | Reset a chat session |
| `POST /api/v1/ai/analyze/team` | Non-streaming team analysis (Claude Sonnet 5) |

FastAPI's interactive docs are available at `/docs`.

---

## How to run the project

The project is designed for the Emergent preview environment (Kubernetes + supervisor). Ports and URLs come from `.env` — never hardcode.

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Frontend

```bash
cd frontend
yarn install
yarn start          # Expo dev server (mobile via Expo Go + web preview)
```

### Tests

```bash
pip install httpx pytest pytest-asyncio
pytest -q
```

---

## Future development phases

See [`documentation/ROADMAP.md`](documentation/ROADMAP.md).
