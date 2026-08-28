# VGC Intelligence — API Reference (Pokémon Data Explorer)

> Phase 3A. All routes are read-only and live under `/api/v1`. Every response is
> served from the **canonical Pokémon Showdown import** (`sd_*` collections),
> scoped to the currently active `import_id`. When no dataset is active the API
> answers `503`.

## Pagination convention

Every paged list shares the same envelope (produced by `routers/v1/_query.paged_list`):

```json
{
  "total": 1517,
  "limit": 50,
  "offset": 0,
  "page": 1,
  "pages": 31,
  "import_id": "<active import id>",
  "items": [ ... ]
}
```

- `limit`: 1–500 (default 50). `offset`: ≥ 0. Values outside bounds → `422`.
- `page` = `offset // limit + 1`; `pages` = `ceil(total / limit)` (0 when empty).

## Endpoints

### `GET /api/v1/pokemon`

Paged Pokémon list.

| Param | Type | Description |
|---|---|---|
| `limit` / `offset` | int | Pagination (see above). |
| `q` | string | Case-insensitive **substring** search on `name`/`slug`. User input is regex-escaped (safe). |
| `type` | string | Case-insensitive exact type filter, e.g. `Steel` or `steel`. |
| `ability` | string | Case-insensitive exact ability filter over every slot (`0`, `1`, `H`, `S`), e.g. `Intimidate`. |
| `only_base` | bool | Exclude alternative formes. |
| `include_special` | bool | Default `false`: entries with `num <= 0` (CAP fan-made Pokémon, Pokestar Studios props, MissingNo.) are excluded from listings. Set `true` to include them. They remain reachable via the detail route. |

Filters combine with AND. Ordering is deterministic: `num` asc, then `name` asc.

### `GET /api/v1/pokemon/{id}`

Full canonical document for one Pokémon plus its raw `learnset` map
(`move_id -> learn source codes`, e.g. `"9M"`, `"9L14"`).

- `{id}` accepts a Showdown id/slug/name (`gholdengo`, `Mr. Mime`) or a dex
  number (`1000`). Names are normalized with Showdown's `toID()` rule.
- When several formes share a dex number, the **base species** is returned.
- `404` when not found.

### `GET /api/v1/pokemon/{id}/abilities`

The Pokémon's ability slots resolved against `sd_abilities`:

```json
{
  "pokemon": "incineroar",
  "name": "Incineroar",
  "total": 2,
  "items": [
    { "slot": "0", "is_hidden": false, "name": "Blaze", "ability": { "name": "Blaze", "rating": 2, ... } },
    { "slot": "H", "is_hidden": true, "name": "Intimidate", "ability": { ... } }
  ]
}
```

### `GET /api/v1/pokemon/{id}/moves`

The Pokémon's learnset resolved against `sd_moves` in a single `$in` query
(no N+1). Sorted by move name. Each item carries `learn_sources`. Move ids
present in the learnset but missing from `sd_moves` are reported in
`unresolved` (normally empty).

## Indexes

Created idempotently at API startup (`backend/indexes.py`): compound indexes
led by `import_id` on `sd_pokemon` (`showdown_id`, `num`, `types`, `is_base`,
`name`), `sd_learnsets`, `sd_moves`, `sd_abilities`, `sd_items`, `sd_natures`,
`sd_types`, `sd_formats`.

## Known canonical-data limitations (not invented by the API)

- **Generation** is not stored per Pokémon in the imported Showdown dataset → no generation filter.
- **Per-Pokémon format legality** is not stored on `sd_pokemon` (formats exist separately in `sd_formats`) → no format filter yet.
- Formes without their own learnset entry return an empty move list (no base-species fallback is fabricated).
- `desc`/`short_desc` on moves/abilities are `null` in the current import (Showdown keeps long text in a separate repo not yet ingested).
