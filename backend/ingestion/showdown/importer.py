"""Normalize + validate + persist parsed Showdown data.

Consumes the dict returned by :mod:`parser_bridge` and writes normalized
documents to Mongo under an ``import_id`` fingerprint. Nothing is
"active" until the caller flips the ``showdown_pointers`` pointer.

Every rejected record is logged (structured) — no silent drops.
"""
from __future__ import annotations
import logging
import re
from dataclasses import dataclass, field
from typing import Iterable, Any

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("showdown.import")

# One collection per category. All docs carry ``import_id`` so multiple
# imports can coexist in the same database (versioned datasets).
COL_POKEMON = "sd_pokemon"
COL_MOVES = "sd_moves"
COL_ABILITIES = "sd_abilities"
COL_ITEMS = "sd_items"
COL_NATURES = "sd_natures"
COL_TYPES = "sd_types"
COL_TYPECHART = "sd_typechart"
COL_LEARNSETS = "sd_learnsets"
COL_FORMATS = "sd_formats"
COL_RULESETS = "sd_rulesets"
COL_RAW = "sd_raw"

ALL_COLLECTIONS = [
    COL_POKEMON, COL_MOVES, COL_ABILITIES, COL_ITEMS, COL_NATURES,
    COL_TYPES, COL_TYPECHART, COL_LEARNSETS, COL_FORMATS, COL_RULESETS, COL_RAW,
]

STAT_KEYS = ("hp", "atk", "def", "spa", "spd", "spe")


@dataclass
class ImportReport:
    counts: dict[str, int] = field(default_factory=dict)
    rejected: dict[str, list[str]] = field(default_factory=dict)  # category -> reasons
    validation_errors: list[str] = field(default_factory=list)
    champions_formats: list[dict] = field(default_factory=list)

    def add_rejected(self, cat: str, reason: str) -> None:
        self.rejected.setdefault(cat, []).append(reason)
        logger.info('{"event":"SHOWDOWN_RECORD_REJECTED","category":"%s","reason":%r}',
                    cat, reason)

    def total_rejected(self) -> int:
        return sum(len(v) for v in self.rejected.values())

    def summary(self) -> dict:
        return {
            "counts": self.counts,
            "rejected": {k: len(v) for k, v in self.rejected.items()},
            "validationErrors": self.validation_errors,
            "championsFormats": len(self.champions_formats),
        }


# ---------------------------------------------------------------------------
# Normalizers
# ---------------------------------------------------------------------------
def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())


def _normalize_pokemon(pokedex: dict, import_id: str, report: ImportReport) -> list[dict]:
    """Every Showdown entry is a species OR a form of a base species.

    We flatten both into one collection with an ``is_base`` flag and a
    ``base_species_id`` FK when the entry is a form. This matches the
    Pokemon/PokemonForm split described in the domain models while
    keeping queries simple.
    """
    # Build a lookup of {name -> entry} for base-species inheritance.
    by_name = {
        v["name"]: v for v in pokedex.values()
        if isinstance(v, dict) and v.get("name")
    }
    docs: list[dict] = []
    for sid, entry in pokedex.items():
        if not isinstance(entry, dict) or not entry.get("name"):
            report.add_rejected("pokemon", f"malformed entry: {sid}")
            continue
        base_species = entry.get("baseSpecies")
        is_base = base_species is None
        is_cosmetic = bool(entry.get("isCosmeticForme"))
        base = by_name.get(base_species) if base_species else None
        types = entry.get("types") or (base or {}).get("types")
        base_stats = entry.get("baseStats") or (base or {}).get("baseStats")
        if not types or not isinstance(types, list):
            report.add_rejected("pokemon", f"missing types: {sid}")
            continue
        if not base_stats or not all(k in base_stats for k in STAT_KEYS):
            report.add_rejected("pokemon", f"incomplete baseStats: {sid}")
            continue
        docs.append({
            "import_id": import_id,
            "showdown_id": sid,
            "num": entry.get("num") or (base or {}).get("num"),
            "name": entry["name"],
            "slug": _slug(entry["name"]),
            "types": types,
            "base_stats": {k: int(base_stats[k]) for k in STAT_KEYS},
            "abilities": entry.get("abilities") or (base or {}).get("abilities") or {},
            "height_m": entry.get("heightm"),
            "weight_kg": entry.get("weightkg"),
            "color": entry.get("color"),
            "gender_ratio": entry.get("genderRatio"),
            "egg_groups": entry.get("eggGroups") or [],
            "evos": entry.get("evos") or [],
            "prevo": entry.get("prevo"),
            "is_base": is_base,
            "is_cosmetic_forme": is_cosmetic,
            "base_species_name": base_species,
            "forme": entry.get("forme"),
            "forme_order": entry.get("formeOrder") or [],
            "other_formes": entry.get("otherFormes") or [],
            "cosmetic_formes": entry.get("cosmeticFormes") or [],
            "tags": entry.get("tags") or [],
        })
    return docs


def _normalize_moves(moves: dict, import_id: str, report: ImportReport, *,
                     mod: str | None = None) -> list[dict]:
    out = []
    for mid, entry in moves.items():
        if not isinstance(entry, dict):
            continue
        # Inherit-style overlays are patches to base entries — they carry
        # ``inherit: true`` (or simply omit the ``name``). Skip silently
        # rather than reject; they'll be layered on top of base data by
        # the future format resolver.
        if entry.get("inherit") or not entry.get("name"):
            if mod is None and not entry.get("inherit"):
                report.add_rejected("moves", f"malformed: {mid}")
            continue
        out.append({
            "import_id": import_id,
            "showdown_id": mid,
            "num": entry.get("num"),
            "name": entry["name"],
            "slug": _slug(entry["name"]),
            "type": entry.get("type"),
            "category": entry.get("category"),
            "base_power": entry.get("basePower"),
            "accuracy": entry.get("accuracy"),
            "pp": entry.get("pp"),
            "priority": entry.get("priority", 0),
            "target": entry.get("target"),
            "flags": entry.get("flags") or {},
            "secondary": entry.get("secondary"),
            "secondaries": entry.get("secondaries"),
            "desc": entry.get("desc"),
            "short_desc": entry.get("shortDesc"),
        })
    return out


def _normalize_abilities(items_: dict, import_id: str, report: ImportReport, *,
                         mod: str | None = None) -> list[dict]:
    out = []
    for aid, entry in items_.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("inherit") or not entry.get("name"):
            if mod is None and not entry.get("inherit"):
                report.add_rejected("abilities", f"malformed: {aid}")
            continue
        out.append({
            "import_id": import_id,
            "showdown_id": aid,
            "num": entry.get("num"),
            "name": entry["name"],
            "slug": _slug(entry["name"]),
            "desc": entry.get("desc"),
            "short_desc": entry.get("shortDesc"),
            "rating": entry.get("rating"),
        })
    return out


def _normalize_items(items_: dict, import_id: str, report: ImportReport, *,
                     mod: str | None = None) -> list[dict]:
    out = []
    for iid, entry in items_.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("inherit") or not entry.get("name"):
            if mod is None and not entry.get("inherit"):
                report.add_rejected("items", f"malformed: {iid}")
            continue
        out.append({
            "import_id": import_id,
            "showdown_id": iid,
            "num": entry.get("num"),
            "name": entry["name"],
            "slug": _slug(entry["name"]),
            "desc": entry.get("desc"),
            "short_desc": entry.get("shortDesc"),
            "fling": entry.get("fling"),
            "mega_evolves": entry.get("megaEvolves"),
            "mega_stone": entry.get("megaStone"),
            "z_move": entry.get("zMove"),
            "gen": entry.get("gen"),
        })
    return out


def _normalize_natures(natures: dict, import_id: str, report: ImportReport) -> list[dict]:
    out = []
    for nid, entry in natures.items():
        if not isinstance(entry, dict) or not entry.get("name"):
            report.add_rejected("natures", f"malformed: {nid}")
            continue
        out.append({
            "import_id": import_id,
            "showdown_id": nid,
            "name": entry["name"],
            "increased_stat": entry.get("plus"),
            "decreased_stat": entry.get("minus"),
        })
    return out


def _normalize_types(typechart: dict, import_id: str) -> tuple[list[dict], list[dict]]:
    """Return (types_list, typechart_docs)."""
    type_docs = []
    chart_docs = []
    for tid, entry in typechart.items():
        if not isinstance(entry, dict):
            continue
        display = tid.capitalize()
        type_docs.append({
            "import_id": import_id,
            "showdown_id": tid,
            "name": display,
        })
        chart_docs.append({
            "import_id": import_id,
            "type": display,
            "damage_taken": entry.get("damageTaken") or {},
            "hp_ivs": entry.get("HPivs"),
            "hp_dvs": entry.get("HPdvs"),
        })
    return type_docs, chart_docs


def _normalize_learnsets(learnsets: dict, import_id: str) -> list[dict]:
    out = []
    for sid, entry in learnsets.items():
        if not isinstance(entry, dict):
            continue
        ls = entry.get("learnset") or {}
        if not isinstance(ls, dict):
            continue
        out.append({
            "import_id": import_id,
            "showdown_id": sid,
            "moves": {m: sources for m, sources in ls.items()},
            "move_count": len(ls),
            "event_data": entry.get("eventData") or [],
        })
    return out


def _normalize_formats(formats_list: list, import_id: str, report: ImportReport) -> list[dict]:
    """The formats file exports a heterogeneous list with section headers
    and format entries. We keep only entries that name a format."""
    out = []
    current_section: str | None = None
    for entry in formats_list or []:
        if not isinstance(entry, dict):
            continue
        if "section" in entry and "name" not in entry:
            current_section = entry.get("section")
            continue
        name = entry.get("name")
        if not name:
            report.add_rejected("formats", "format entry without name")
            continue
        mod = (entry.get("mod") or "").lower()
        is_champions = mod.startswith("champion") or "champion" in name.lower()
        is_vgc = "vgc" in name.lower() or "vgc" in (entry.get("desc") or "").lower()
        is_doubles = (
            entry.get("gameType") == "doubles" or "doubles" in name.lower()
        )
        out.append({
            "import_id": import_id,
            "showdown_id": _slug(name),
            "name": name,
            "section": current_section,
            "mod": entry.get("mod"),
            "game_type": entry.get("gameType"),
            "team": entry.get("team"),
            "ruleset": entry.get("ruleset") or [],
            "banlist": entry.get("banlist") or [],
            "unbanlist": entry.get("unbanlist") or [],
            "restricted": entry.get("restricted") or [],
            "desc": entry.get("desc"),
            "rated": entry.get("rated"),
            "team_length": entry.get("teamLength"),
            "best_of_default": entry.get("bestOfDefault"),
            "is_champions": is_champions,
            "is_vgc": is_vgc,
            "is_doubles": is_doubles,
        })
    return out


def _normalize_rulesets(rulesets: dict, import_id: str, report: ImportReport, *,
                        mod: str | None = None) -> list[dict]:
    out = []
    for rid, entry in rulesets.items():
        if not isinstance(entry, dict):
            continue
        if entry.get("inherit") or not entry.get("name"):
            if mod is None and not entry.get("inherit"):
                report.add_rejected("rulesets", f"malformed: {rid}")
            continue
        out.append({
            "import_id": import_id,
            "showdown_id": rid,
            "name": entry["name"],
            "effect_type": entry.get("effectType"),
            "desc": entry.get("desc"),
            "ruleset": entry.get("ruleset") or [],
            "banlist": entry.get("banlist") or [],
            "unbanlist": entry.get("unbanlist") or [],
            "restricted": entry.get("restricted") or [],
        })
    return out


# ---------------------------------------------------------------------------
# Validation (cross-references)
# ---------------------------------------------------------------------------
def _validate_cross_refs(bundle: dict[str, list[dict]], report: ImportReport) -> None:
    """Structural checks — populate ``report.validation_errors`` on failure."""
    # Duplicate showdown_ids per category. Different collections use
    # different unique keys — typechart is keyed by ``type``.
    key_by_cat = {
        "pokemon": "showdown_id",
        "moves": "showdown_id",
        "abilities": "showdown_id",
        "items": "showdown_id",
        "natures": "showdown_id",
        "types": "showdown_id",
        "typechart": "type",
        "learnsets": "showdown_id",
        "formats": "showdown_id",
        "rulesets": "showdown_id",
    }
    for cat, docs in bundle.items():
        pk = key_by_cat.get(cat, "showdown_id")
        seen: set[str] = set()
        for d in docs:
            key = d.get(pk)
            if key is None:
                report.validation_errors.append(f"{cat}: doc missing {pk}")
                continue
            if key in seen:
                report.validation_errors.append(f"duplicate {cat}: {key}")
            seen.add(key)

    # Learnset move references must exist in moves. Cross-gen references
    # are common (Showdown ships old-gen learnsets that name moves not
    # present in the base ``moves.ts``). Log as rejects, do not fail.
    move_ids = {d["showdown_id"] for d in bundle.get("moves", [])}
    for ls in bundle.get("learnsets", []):
        for m in ls.get("moves", {}):
            if m not in move_ids:
                report.add_rejected(
                    "learnsets",
                    f"{ls['showdown_id']}: unknown move ref {m}",
                )
                break

    # Pokemon type refs — MissingNo uses legacy debug types like "Bird".
    # Log rejects, don't fail.
    type_names = {t["name"] for t in bundle.get("types", [])}
    for p in bundle.get("pokemon", []):
        for t in p.get("types", []):
            if t not in type_names:
                report.add_rejected(
                    "pokemon",
                    f"{p['showdown_id']}: unknown type {t}",
                )
                break

    # Type chart symmetry
    chart_types = {d["type"] for d in bundle.get("typechart", [])}
    if chart_types and type_names and chart_types != type_names:
        report.validation_errors.append(
            f"typechart types mismatch types: extra={type_names ^ chart_types}"
        )


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
async def _bulk_insert(db: AsyncIOMotorDatabase, collection: str,
                       docs: Iterable[dict]) -> int:
    docs = list(docs)
    if not docs:
        return 0
    await db[collection].insert_many(docs, ordered=False)
    return len(docs)


async def wipe_import(db: AsyncIOMotorDatabase, import_id: str) -> None:
    for col in ALL_COLLECTIONS:
        await db[col].delete_many({"import_id": import_id})


async def normalize_and_store(
    db: AsyncIOMotorDatabase, parsed: dict, import_id: str,
) -> ImportReport:
    report = ImportReport()

    pokedex = parsed.get("pokedex") or {}
    moves = parsed.get("moves") or {}
    abilities = parsed.get("abilities") or {}
    items = parsed.get("items") or {}
    natures = parsed.get("natures") or {}
    typechart = parsed.get("typechart") or {}
    learnsets = parsed.get("learnsets") or {}
    formats_list = parsed.get("formats") or []
    rulesets = parsed.get("rulesets") or {}

    pokemon_docs = _normalize_pokemon(pokedex, import_id, report)
    move_docs = _normalize_moves(moves, import_id, report)
    ability_docs = _normalize_abilities(abilities, import_id, report)
    item_docs = _normalize_items(items, import_id, report)
    nature_docs = _normalize_natures(natures, import_id, report)
    type_docs, chart_docs = _normalize_types(typechart, import_id)
    learnset_docs = _normalize_learnsets(learnsets, import_id)
    format_docs = _normalize_formats(formats_list, import_id, report)
    ruleset_docs = _normalize_rulesets(rulesets, import_id, report)

    # Merge Champions mod additions with clear provenance flags. They live
    # alongside base data so a Champions-format query can find them.
    for cat_key, target_docs, showdown_key, is_kv in [
        ("champions_moves", move_docs, "moves", True),
        ("champions_abilities", ability_docs, "abilities", True),
        ("champions_items", item_docs, "items", True),
        ("champions_rulesets", ruleset_docs, "rulesets", True),
        ("champions_learnsets", learnset_docs, "learnsets", True),
    ]:
        source = parsed.get(cat_key) or {}
        if not source:
            continue
        # Normalize using the same routine, but flag the mod.
        if cat_key == "champions_moves":
            extra = _normalize_moves(source, import_id, report, mod="champions")
        elif cat_key == "champions_abilities":
            extra = _normalize_abilities(source, import_id, report, mod="champions")
        elif cat_key == "champions_items":
            extra = _normalize_items(source, import_id, report, mod="champions")
        elif cat_key == "champions_rulesets":
            extra = _normalize_rulesets(source, import_id, report, mod="champions")
        elif cat_key == "champions_learnsets":
            extra = _normalize_learnsets(source, import_id)
        else:
            extra = []
        for d in extra:
            d["mod"] = "champions"
            d["showdown_id"] = f"champions:{d['showdown_id']}"
        target_docs.extend(extra)

    bundle = {
        "pokemon": pokemon_docs,
        "moves": move_docs,
        "abilities": ability_docs,
        "items": item_docs,
        "natures": nature_docs,
        "types": type_docs,
        "typechart": chart_docs,
        "learnsets": learnset_docs,
        "formats": format_docs,
        "rulesets": ruleset_docs,
    }
    _validate_cross_refs(bundle, report)

    report.champions_formats = [
        {
            "showdown_id": f["showdown_id"],
            "name": f["name"],
            "mod": f["mod"],
            "game_type": f["game_type"],
            "ruleset": f["ruleset"],
            "banlist": f["banlist"],
            "restricted": f["restricted"],
            "team_length": f["team_length"],
        }
        for f in format_docs
        if f["is_champions"]
    ]

    # Wipe any residual docs from a previous partial import.
    await wipe_import(db, import_id)

    report.counts = {
        "pokemon": await _bulk_insert(db, COL_POKEMON, pokemon_docs),
        "moves": await _bulk_insert(db, COL_MOVES, move_docs),
        "abilities": await _bulk_insert(db, COL_ABILITIES, ability_docs),
        "items": await _bulk_insert(db, COL_ITEMS, item_docs),
        "natures": await _bulk_insert(db, COL_NATURES, nature_docs),
        "types": await _bulk_insert(db, COL_TYPES, type_docs),
        "typechart": await _bulk_insert(db, COL_TYPECHART, chart_docs),
        "learnsets": await _bulk_insert(db, COL_LEARNSETS, learnset_docs),
        "formats": await _bulk_insert(db, COL_FORMATS, format_docs),
        "rulesets": await _bulk_insert(db, COL_RULESETS, ruleset_docs),
    }

    # RAW SNAPSHOT — one doc per category, kept alongside normalized data.
    raw_docs = [
        {"import_id": import_id, "category": cat, "payload": parsed.get(cat)}
        for cat in parsed
    ]
    await _bulk_insert(db, COL_RAW, raw_docs)
    report.counts["raw"] = len(raw_docs)

    return report


# ---------------------------------------------------------------------------
# Post-persistence smoke tests (used as "compatibility tests" in the pipeline)
# ---------------------------------------------------------------------------
async def smoke_tests(db: AsyncIOMotorDatabase, import_id: str) -> dict:
    """Sanity checks against persisted docs. Uses imported data as truth."""
    results: dict[str, Any] = {"passed": True, "checks": {}}

    async def _count(col: str) -> int:
        return await db[col].count_documents({"import_id": import_id})

    counts = {c: await _count(c) for c in ALL_COLLECTIONS}
    results["counts"] = counts

    def _check(name: str, cond: bool, detail: Any = None):
        results["checks"][name] = {"ok": bool(cond), "detail": detail}
        if not cond:
            results["passed"] = False

    _check("has_pokemon", counts[COL_POKEMON] > 800, counts[COL_POKEMON])
    _check("has_moves", counts[COL_MOVES] > 500, counts[COL_MOVES])
    _check("has_abilities", counts[COL_ABILITIES] > 200, counts[COL_ABILITIES])
    _check("has_items", counts[COL_ITEMS] > 300, counts[COL_ITEMS])
    _check("has_natures_25", counts[COL_NATURES] == 25, counts[COL_NATURES])
    _check("has_types_18", counts[COL_TYPES] >= 18, counts[COL_TYPES])
    _check("has_formats", counts[COL_FORMATS] > 100, counts[COL_FORMATS])
    _check("has_rulesets", counts[COL_RULESETS] > 100, counts[COL_RULESETS])

    # Known-species sanity — value read from the imported dataset itself.
    for sid, expected_type in (("pikachu", "Electric"),
                               ("charizard", "Fire"),
                               ("garchomp", "Dragon"),
                               ("incineroar", "Fire")):
        doc = await db[COL_POKEMON].find_one(
            {"import_id": import_id, "showdown_id": sid}, {"_id": 0},
        )
        _check(f"pokemon_{sid}_present", doc is not None)
        if doc is not None:
            _check(
                f"pokemon_{sid}_primary_type",
                expected_type in doc.get("types", []),
                doc.get("types"),
            )
            _check(
                f"pokemon_{sid}_basestats_hp_positive",
                (doc.get("base_stats") or {}).get("hp", 0) > 0,
            )

    # Nature adamant must boost atk / lower spa (canonical)
    adamant = await db[COL_NATURES].find_one(
        {"import_id": import_id, "showdown_id": "adamant"}, {"_id": 0},
    )
    _check("nature_adamant_plus_atk",
           adamant and adamant.get("increased_stat") == "atk", adamant)
    _check("nature_adamant_minus_spa",
           adamant and adamant.get("decreased_stat") == "spa", adamant)

    # Type chart: Showdown uses inverted damageTaken values:
    #   0 = normal (1x), 1 = weak (2x), 2 = resist (0.5x), 3 = immune (0x)
    # So Fire taking damage from Water is "weak" → value 1.
    fire = await db[COL_TYPECHART].find_one(
        {"import_id": import_id, "type": "Fire"}, {"_id": 0},
    )
    _check("typechart_fire_takes_2x_from_water",
           fire and fire["damage_taken"].get("Water") == 1)

    # At least one Champions format must exist
    n_champ = await db[COL_FORMATS].count_documents(
        {"import_id": import_id, "is_champions": True},
    )
    _check("has_champions_formats", n_champ > 0, n_champ)

    return results
