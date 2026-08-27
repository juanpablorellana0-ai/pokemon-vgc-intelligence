# Data Sources

VGC Intelligence never modifies upstream sources. Every source is treated as an
external dependency, tracked by a dedicated adapter and its own synchronization
history.

## Pokémon Showdown

- **Repository URL**: `https://github.com/smogon/pokemon-showdown.git`
- **Branch tracked**: `master` (configurable via `SHOWDOWN_BRANCH`)
- **License**: MIT — see the upstream `LICENSE` file at
  <https://github.com/smogon/pokemon-showdown/blob/master/LICENSE>
- **Purpose**: canonical reference for species, moves, abilities, items, and
  type/ability effect data used by the future deterministic damage engine and
  the frontend Pokémon browser.

### Access model

- The repository is **public**. The application accesses it anonymously using
  `git ls-remote` — no GitHub token, no credentials, no OAuth.
- The user's GitHub integration is **only** for this application's own
  repository. It is **not** used to reach Pokémon Showdown.

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
 [3] fetch new commit (only if SHOWDOWN_ENABLE_CLONE=1)
        │
        ▼
 [4] parse / normalize   (deferred — importer ships in a later phase)
        │
        ▼
 [5] validate            (schema + integrity)
        │
        ▼
 [6] compatibility tests (regression + shape guards)
        │
        ▼
 [7] create versioned dataset directory (showdown_dataset_<sha[:12]>)
        │
        ▼
 [8] activate — only if all previous checks pass
```

Two datasets are always kept on disk: the **active** one and the previous
known-good one (rollback candidate). The active dataset is **never** overwritten
before validation and tests pass.

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
`_id = "showdown_active_dataset"`) always identifies exactly one active commit
and up to one rollback candidate.

### Admin API

Protected via `X-Admin-Token` header (`ADMIN_TOKEN` env var). The endpoints are
**not** publicly accessible.

| Endpoint                                | Purpose                                |
|-----------------------------------------|----------------------------------------|
| `GET /api/v1/admin/showdown/status`     | Data health report                     |
| `POST /api/v1/admin/showdown/check`     | Peek at remote HEAD, no side effects   |
| `POST /api/v1/admin/showdown/sync`      | Run the full sync pipeline             |
| `POST /api/v1/admin/showdown/rollback`  | Switch active pointer to previous ver. |

### Scheduling

Manual triggers are exposed today. A scheduled check every 6 hours (default,
configurable via `SHOWDOWN_SYNC_INTERVAL_HOURS` in a later phase) will call
`/check` first and only run `/sync` when a new commit is available.

### Attribution

Pokémon Showdown is © its contributors and released under the MIT license. Any
data derived from it will carry a footer/credits reference to the upstream
project and its license.

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
