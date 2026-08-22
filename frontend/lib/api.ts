/*
 * Typed API client for Project Anromi.
 * Mirrors every endpoint the Discord bot uses. Zero game logic here —
 * this file is transport only.
 */

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  constructor(public status: number, detail: string) {
    super(detail);
  }
}

async function req<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail =
      typeof data === "object" && data !== null && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : `HTTP ${res.status}`;
    throw new ApiError(res.status, detail);
  }
  return data as T;
}

// ── Types ────────────────────────────────────────────────────────────

export interface Profile {
  id: number;
  discord_id: string;
  username: string;
  dao_title: string;
  realm: number;
  realm_name_en: string;
  realm_name_cn: string;
  stage: string;
  is_bottleneck: boolean;
  spirit_energy: number;
  max_energy: number;
  qi_purity: number;
  meridian_damage: number;
  lifespan_current_years: number;
  lifespan_max_years: number;
  dao_heart_stability: number;
  karma_sin: number;
  spiritual_root: string;
  spiritual_root_purity: number;
  physique_tier: number;
  physique_name: string;
  is_dead: boolean;
  is_remnant_soul: boolean;
  soul_state: string;
  remnant_soul_vitality: number;
  lineage_generation: number;
  death_count: number;
  karmic_legacy_tokens: number;
  streak_days: number;
  best_streak: number;
  dao_insight: number;
  highest_realm_achieved: number;
  total_meditations: number;
  total_breakthrough_wins: number;
  total_breakthrough_fails: number;
  spirit_stones: number;
  luck_stat: number;
  pill_toxicity: number;
  stored_breakthrough_bonus: number;
  alchemy_level: number;
  alchemy_title: string | null;
  forging_level: number;
  forging_title: string | null;
}

export interface MeditateResult {
  message: string;
  qi_gathered: number;
  spirit_energy: number;
  max_energy: number;
  can_breakthrough: boolean;
  streak_days: number;
  streak_multiplier: number;
  deviation_triggered: boolean;
  windfall: { message: string; insight: number; spirit_stones: number } | null;
}

export interface Odds {
  can_attempt: boolean;
  is_realm_leap: boolean;
  base_chance: number;
  final_chance: number;
  target_realm: number;
  target_stage: string;
  reason?: string;
}

export interface BreakthroughResult {
  success: boolean;
  outcome: string;
  message: string;
  roll?: number;
  needed?: number;
  realm: number;
  realm_name_en: string;
  stage: string;
  near_miss: boolean;
  soul_fate?: string;
}

export interface DaoHeart {
  dao_heart_stability: number;
  status: string;
  deviation_risk_chance: number;
  karma_sin: number;
  karma_class: string;
  message: string;
}

export interface BagEntry {
  item_id: string;
  name: string;
  category: string;
  quality: string | null;
  quantity: number;
  base_price: number;
}
export interface Bag {
  discord_id: string;
  spirit_stones: number;
  pill_toxicity: number;
  entries: BagEntry[];
  message: string;
}

export interface RecipeInfo {
  id: string;
  name: string;
  tier: number;
  min_realm: number;
  alchemy_level_req: number;
  base_impurity: number;
  materials: Record<string, number>;
  effects: Record<string, number>;
  blurb: string;
  craftable_now: boolean;
}
export interface RecipesResponse {
  alchemy_level: number;
  alchemy_title: string;
  recipes: RecipeInfo[];
}

export interface RefineResult {
  grade: string | null;
  impurity: number | null;
  heavenly_coincidence: boolean;
  message: string;
  mastery: { level: number; title: string; exp: number };
}

export interface Blueprint {
  id: string;
  name: string;
  slot: string;
  tier: string;
  passive_qi_bonus: number;
  tribulation_resistance: number;
  forging_level_req: number;
  materials: Record<string, number>;
}

export interface CraftResult {
  success: boolean;
  chance: number;
  message: string;
  mastery: { level: number; title: string };
}

export interface EquipResult {
  success: boolean;
  message: string;
  equipped: Record<string, string | null>;
}

export interface NodeNeighbor {
  id: string;
  name: string;
  region: string;
  danger_tier: number;
  travel_cooldown_minutes: number;
  qi_cost_pct: number;
}
export interface WorldMap {
  current_node: {
    id: string;
    name: string;
    region: string;
    plane: string;
    spirit_density: number;
    elemental_bias: string;
    danger_tier: number;
    description: string;
  };
  neighbors: NodeNeighbor[];
  travel_locked_until: string | null;
  message: string;
}

export interface ExploreResult {
  encounter: string;
  message: string;
  cooldown_minutes: number;
}

export interface TribSummary {
  target_realm: number;
  tier: string;
  total_strikes: number;
  strikes_endured: number;
  waves_remaining: number;
  qi_pool: number;
  body_pool: number;
  shield: number;
  dao_heart: number;
  meridian_damage: number;
  gear: Record<string, string | null>;
}
export interface TribState {
  active: boolean;
  summary?: TribSummary;
  log_tail: string[];
  message: string;
}
export interface TribActionResult {
  outcome: "ONGOING" | "SURVIVED" | "DESTROYED" | "BAILED" | "INVALID";
  events: string[];
  summary?: TribSummary;
  realm_advanced_to?: number;
  soul_fate?: string;
  destroyed_artifacts: string[];
}

export interface SoulState {
  soul_state: string;
  remnant_soul_vitality: number;
  hours_as_soul: number;
  karmic_legacy_tokens: number;
  lineage_generation: number;
  death_count: number;
  message: string;
}

export interface ReincarnateResult {
  message: string;
  tokens_spent: number;
  root_luck_bonus: number;
  starting_stone_bonus: number;
  lineage_generation: number;
}

export interface MerchantStall {
  item_id: string;
  name: string;
  price_low_stones: number;
}
export interface MerchantResponse {
  date_utc: string;
  stalls: MerchantStall[];
  message: string;
}

export interface TradeResult {
  success: boolean;
  message: string;
  spirit_stones: number;
}

export interface EventItem {
  id: number;
  discord_id: string;
  username: string;
  event_type: string;
  payload: Record<string, unknown>;
  created_at: string | null;
}

export interface NarrationStatus {
  persona: string;
  configured_providers: string[];
  message: string;
}

// ── Endpoints ────────────────────────────────────────────────────────

export const api = {
  register: (discordId: string, username: string) =>
    req<Profile>("POST", "/api/cultivator/register", { discord_id: discordId, username }),

  profile: (did: string) => req<Profile>("GET", `/api/cultivator/profile/${did}`),

  meditate: (did: string) => req<MeditateResult>("POST", `/api/cultivator/meditate/${did}`),

  odds: (did: string) => req<Odds>("GET", `/api/cultivator/breakthrough-odds/${did}`),

  breakthrough: (did: string) =>
    req<BreakthroughResult>("POST", `/api/cultivator/breakthrough/${did}`, { pill_bonus: 0 }),

  daoHeart: (did: string) => req<DaoHeart>("GET", `/api/cultivator/dao-heart/${did}`),

  bag: (did: string) => req<Bag>("GET", `/api/inventory/bag/${did}`),

  consume: (did: string, itemId: string, quality?: string) =>
    req<{ message: string }>("POST", `/api/inventory/consume/${did}`, {
      item_id: itemId,
      quality: quality ?? undefined,
    }),

  recipes: (did: string) => req<RecipesResponse>("GET", `/api/alchemy/recipes/${did}`),

  refine: (did: string, recipeId: string, furnace: string, flame: string) =>
    req<RefineResult>("POST", `/api/alchemy/refine/${did}`, {
      recipe_id: recipeId,
      furnace_item_id: furnace,
      flame_item_id: flame,
    }),

  blueprints: () => req<Blueprint[]>("GET", "/api/forging/blueprints"),

  craft: (did: string, artifactId: string) =>
    req<CraftResult>("POST", `/api/forging/craft/${did}`, { artifact_id: artifactId }),

  equip: (did: string, slot: string, itemId: string | null) =>
    req<EquipResult>("POST", `/api/forging/equip/${did}`, { slot, item_id: itemId }),

  map: (did: string) => req<WorldMap>("GET", `/api/world/map/${did}`),

  travel: (did: string, targetNodeId: string) =>
    req<{ success: boolean; message: string }>("POST", `/api/world/travel/${did}`, {
      target_node_id: targetNodeId,
    }),

  explore: (did: string, ambushChoice?: string) =>
    req<ExploreResult>("POST", `/api/world/explore/${did}`, {
      ambush_choice: ambushChoice ?? undefined,
    }),

  merchant: (did: string) => req<MerchantResponse>("GET", `/api/economy/merchant/${did}`),

  buy: (did: string, itemId: string) =>
    req<TradeResult>("POST", `/api/economy/buy/${did}`, { item_id: itemId }),

  sell: (did: string, itemId: string, quantity: number) =>
    req<TradeResult>("POST", `/api/economy/sell/${did}`, { item_id: itemId, quantity }),

  convert: (did: string, direction: string, grade: string, amount: number) =>
    req<TradeResult>("POST", `/api/economy/convert/${did}`, { direction, grade, amount }),

  soulState: (did: string) => req<SoulState>("GET", `/api/soul/state/${did}`),

  possess: (did: string, targetName: string, targetStrength: number) =>
    req<SoulState>("POST", `/api/soul/possess/${did}`, {
      target_name: targetName,
      target_strength: targetStrength,
    }),

  reincarnate: (did: string) => req<ReincarnateResult>("POST", `/api/soul/reincarnate/${did}`),

  tribulationState: (did: string) => req<TribState>("GET", `/api/tribulation/state/${did}`),

  tribulationAction: (did: string, action: string) =>
    req<TribActionResult>("POST", `/api/tribulation/action/${did}`, { action }),

  narrationStatus: () => req<NarrationStatus>("GET", "/api/narration/status"),

  narrate: (did: string, eventType: string) =>
    req<{ narration: string; provider: string | null; fell_back: boolean }>(
      "POST",
      `/api/narration/narrate/${did}`,
      { event_type: eventType }
    ),

  events: (sinceId = 0) =>
    req<{ events: EventItem[]; last_id: number }>(
      "GET",
      `/api/narration/events/recent?since_id=${sinceId}&limit=50`
    ),
};
