# Data Sources

VGC Intelligence never modifies upstream sources. Every source is treated as an
external dependency, tracked by a dedicated adapter and its own synchronization
history.

## Pokémon Showdown

- **Repository URL**: `https://github.com/smogon/pokemon-showdown.git`
- **Branch tracked**: `master` (configurable via `SHOWDOWN_BRANCH`)
- **License**: MIT — see the upstream `LICENSE` file at
  <https://github.com/smogon/pokemon-showdown/blob/master/LICENSE>
- **Purpose**: canonical reference for species, moves, abilities, items, natures,
  learnsets, type chart, formats, rulesets and Champions-mod data used by the
  application. Pokémon Showdown is our **primary technical data source**.

### Currently imported commit

The initial canonical import in Phase 2B is pinned to:

    5e8ead64b366aa55b83be979dd3d1050115e8bfe

This SHA was recorded during the successful connectivity test (Phase 2A verify)
and re-imported deterministically via
`POST /api/v1/admin/showdown/sync?commit=<sha>&force=true`.

### Access model

- The repository is **public**. The application accesses it anonymously using
  `git ls-remote` + `git clone` — no GitHub token, no credentials, no OAuth.
- The user's GitHub integration is **only** for this application's own
  repository. It is **not** used to reach Pokémon Showdown.

### Categories imported

Every category is normalized into its own Mongo collection and carries the
`import_id` of the sync that produced it (versioned datasets):

| Category           | Collection        | Source file(s)                                     |
|--------------------|-------------------|----------------------------------------------------|
| Pokémon species    | `sd_pokemon`      | `data/pokedex.ts`                                  |
| Forms              | `sd_pokemon`      | (same; flattened with `is_base`, `is_cosmetic_forme`, `base_species_name`) |
| Types              | `sd_types`        | derived from `data/typechart.ts`                   |
| Type chart         | `sd_typechart`    | `data/typechart.ts`                                |
| Base stats         | inside `sd_pokemon.base_stats` | `data/pokedex.ts`                       |
| Abilities          | `sd_abilities`    | `data/abilities.ts` (+ Champions overlay)          |
| Moves              | `sd_moves`        | `data/moves.ts` (+ Champions overlay)              |
| Items              | `sd_items`        | `data/items.ts` (+ Champions overlay)              |
| Natures            | `sd_natures`      | `data/natures.ts`                                  |
| Learnsets          | `sd_learnsets`    | `data/learnsets.ts` (+ Champions overlay)          |
| Formats            | `sd_formats`      | `config/formats.ts`                                |
| Rulesets           | `sd_rulesets`     | `data/rulesets.ts` (+ Champions overlay)           |
| Champions formats  | `sd_formats` where `is_champions=true` | subset of above                |
| RAW snapshot       | `sd_raw`          | full per-category dumps preserved alongside normalized data |

Base stats live inside `sd_pokemon.base_stats` (dict) and are **kept separate
from any battle stat calculation** — the future deterministic damage engine
consumes them from there without mutating.

### Synchronization architecture

```
Showdown Git Repository (public)
        │
        ▼
 [1] check remote commit (git ls-remote)
        │
        ▼
 [2] compare with active commit
        │
        ├── unchanged  → stop, status=up_to_date
        │
        ▼
 [3] fetch new commit (git clone --quiet + git checkout <sha>)
        │
        ▼
 [4] parse       (Node + esbuild strip TS → JSON; RAW snapshot preserved on disk and in Mongo)
        │
        ▼
 [5] normalize   (per-category Python normalizers with cross-refs)
        │
        ▼
 [6] validate    (duplicate ids, cross-ref checks; broken refs are logged as rejects, not silent drops)
        │
        ▼
 [7] persist     (insert into `sd_*` collections with `import_id`)
        │
        ▼
 [8] compatibility tests (deterministic assertions read FROM the imported dataset)
        │
        ▼
 [9] activate — only if all previous checks pass (flip `showdown_pointers.activeImportId`)
```

Two datasets are always kept alongside each other in the DB: the **active**
one and the previous known-good one (rollback candidate). The active pointer
is **never** flipped before validation and tests pass. On failure the
previously active dataset stays active.

### Locking

A single Mongo document with `_id = "showdown_sync_lock"` acts as an advisory
lock. Two synchronization jobs can never run at the same time. Locks older than
30 minutes are considered stale and are broken automatically.

### Version pinning

Every sync attempt records, in the `showdown_sync_history` collection:

- `repositoryUrl`, `branch`
- `previousCommit`, `newCommit`
- `startedAt`, `completedAt`, `duration_ms`
- `status`
- `recordsDiscovered`, `recordsImported`, `recordsUpdated`, `recordsRejected`
- `validationErrors`, `testResults`
- `activated`
- `errorMessage`
- `importerVersion`, `appVersion`

The active dataset pointer (`showdown_pointers` collection,
`_id = "showdown_active_dataset"`) always identifies exactly one active commit,
its `activeImportId`, and up to one rollback candidate (`previousImportId`).

### Admin API

Protected via `X-Admin-Token` header (`ADMIN_TOKEN` env var). Not publicly
accessible.

| Endpoint                                | Purpose                                          |
|-----------------------------------------|--------------------------------------------------|
| `GET /api/v1/admin/showdown/status`     | Data health report                               |
| `POST /api/v1/admin/showdown/check`     | Peek at upstream HEAD, no side effects           |
| `POST /api/v1/admin/showdown/sync`      | Run the sync pipeline (optional `?commit=<sha>&force=true`) |
| `POST /api/v1/admin/showdown/rollback`  | Restore previous dataset                         |

### Public read API

Consumed by the application (and third parties) — no auth required for reads
in this phase:

| Endpoint                     | Notes                                            |
|------------------------------|--------------------------------------------------|
| `GET /api/v1/pokemon`        | Paginated (`limit`, `offset`, `only_base`, `q`)  |
| `GET /api/v1/pokemon/{id}`   | By showdown_id or dex number; includes learnset  |
| `GET /api/v1/moves`          | Paginated + filter by `type`, `category`, `q`    |
| `GET /api/v1/abilities`      | Paginated + `q`                                  |
| `GET /api/v1/items`          | Paginated + `q`                                  |
| `GET /api/v1/natures`        | 25 canonical natures                             |
| `GET /api/v1/types`          | 19 types (18 official + Stellar)                 |
| `GET /api/v1/types/chart`    | Full effectiveness chart                         |
| `GET /api/v1/formats`        | Paginated + `vgc`, `champions`, `doubles`, `mod` |
| `GET /api/v1/rulesets`       | Paginated                                        |
| `GET /api/v1/regulations`    | VGC formats whose name contains a Regulation letter |

Every list endpoint returns `{total, limit, offset, import_id, items}` and
transparently filters by the currently active `import_id`.

### Scheduling

Manual triggers are exposed today. A scheduled check every 6 hours (default,
configurable via `SHOWDOWN_SYNC_INTERVAL_HOURS` in a later phase) will call
`/check` first and only run `/sync` when a new commit is available.

### Attribution

Pokémon Showdown is © its contributors and released under the MIT license.
Everything derived from it in the application (data, API responses, UI) will
carry a footer/credits reference to the upstream project and its license.

---

## Future sources (planned adapters — not yet connected)

Each will follow the same isolation contract: dedicated adapter, dedicated
synchronization history collection, dedicated dataset directory, dedicated
license note in this file.

- Pikalytics
- MunchStats
- champions.karthikb.dev (Replica Teams)
- LabMaus
- ReportWorm
- Cut Explorer
- VGC Guide
