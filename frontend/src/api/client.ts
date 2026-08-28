/**
 * Minimal typed API client for the VGC Intelligence backend.
 * All routes live under `${EXPO_PUBLIC_BACKEND_URL}/api/v1`.
 */

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

const BASE = `${process.env.EXPO_PUBLIC_BACKEND_URL ?? ''}/api/v1`;

type Params = Record<string, string | number | boolean | null | undefined>;

export async function apiGet<T>(path: string, params?: Params): Promise<T> {
  const parts: string[] = [];
  Object.entries(params ?? {}).forEach(([k, v]) => {
    if (v === undefined || v === null || v === '') return;
    parts.push(`${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`);
  });
  const url = `${BASE}${path}${parts.length ? `?${parts.join('&')}` : ''}`;
  let res: Response;
  try {
    res = await fetch(url);
  } catch {
    throw new ApiError(0, 'network error');
  }
  if (!res.ok) {
    let detail = `HTTP ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = String(body.detail);
    } catch {
      // non-JSON error body — keep the HTTP status message
    }
    throw new ApiError(res.status, detail);
  }
  return (await res.json()) as T;
}

// ---- Response shapes (mirror backend/routers/v1) ----

export interface Paged<T> {
  total: number;
  limit: number;
  offset: number;
  page: number;
  pages: number;
  import_id: string;
  items: T[];
}

export interface BaseStats {
  hp: number;
  atk: number;
  def: number;
  spa: number;
  spd: number;
  spe: number;
}

export interface PokemonSummary {
  showdown_id: string;
  num: number;
  name: string;
  slug: string;
  types: string[];
  base_stats: BaseStats;
  abilities: Record<string, string>;
  is_base: boolean;
  forme: string | null;
  base_species_name: string | null;
}

export interface PokemonDetail extends PokemonSummary {
  height_m: number | null;
  weight_kg: number | null;
  color: string | null;
  egg_groups: string[];
  evos: string[];
  prevo: string | null;
  other_formes: string[];
  cosmetic_formes: string[];
  tags: string[];
  learnset: Record<string, string[]>;
}

export interface AbilitySlot {
  slot: string;
  is_hidden: boolean;
  name: string;
  ability: {
    showdown_id: string;
    name: string;
    rating: number | null;
    desc: string | null;
    short_desc: string | null;
  } | null;
}

export interface PokemonAbilities {
  pokemon: string;
  name: string;
  total: number;
  items: AbilitySlot[];
}

export interface MoveEntry {
  showdown_id: string;
  name: string;
  type: string;
  category: string;
  base_power: number | null;
  accuracy: number | boolean | null;
  pp: number | null;
  learn_sources: string[];
}

export interface PokemonMoves {
  pokemon: string;
  name: string;
  total: number;
  items: MoveEntry[];
  unresolved: string[];
}

export interface TypeInfo {
  showdown_id: string;
  name: string;
}
