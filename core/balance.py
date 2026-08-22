"""
═══════════════════════════════════════════════════════════════════
 ANROMI MASTER BALANCE FILE
═══════════════════════════════════════════════════════════════════
 Every tunable number in the game lives HERE. Edit values freely —
 no logic changes required. Engines read this file at call time.
═══════════════════════════════════════════════════════════════════
"""
from typing import Any, Dict, Optional

# ───────────────────────────────────────────────────────────────────
# SPIRITUAL ROOTS (Linggen) — roll_weight values are relative (%).
# absorption_multiplier scales meditation Qi gain.
# purity_range = [min, max] rolled purity on character creation.
# ───────────────────────────────────────────────────────────────────
ROOTS = {
    "Mortal Five-Element": {
        "rarity": "Common",
        "elements": ["Metal", "Wood", "Water", "Fire", "Earth"],
        "absorption_multiplier": 0.5,
        "roll_weight": 25.0,
        "purity_range": (0.30, 0.50),
        "blurb": "Five muddled elements fight for dominance. A slow road.",
    },
    "Pseudo Four-Element": {
        "rarity": "Common",
        "elements": ["Metal", "Wood", "Water", "Earth"],
        "absorption_multiplier": 0.8,
        "roll_weight": 25.0,
        "purity_range": (0.40, 0.55),
        "blurb": "Four impure elements. Barely acceptable talent.",
    },
    "True Three-Element": {
        "rarity": "Uncommon",
        "elements": ["Fire", "Water", "Earth"],
        "absorption_multiplier": 1.2,
        "roll_weight": 30.0,
        "purity_range": (0.50, 0.65),
        "blurb": "Three harmonized elements. A respectable foundation.",
    },
    "Dual Elemental": {
        "rarity": "Rare",
        "elements": ["Fire", "Lightning"],
        "absorption_multiplier": 1.8,
        "roll_weight": 14.0,
        "purity_range": (0.65, 0.80),
        "blurb": "Two elements in rare accord. Sects will notice you.",
    },
    "Heaven Single-Element": {
        "rarity": "Epic",
        "elements": ["Fire"],
        "absorption_multiplier": 3.0,
        "roll_weight": 3.5,
        "purity_range": (0.90, 0.98),
        "blurb": "A single flawless element. Heaven-blessed genius.",
    },
    "Mutant Lightning": {
        "rarity": "Legendary",
        "elements": ["Lightning"],
        "absorption_multiplier": 3.5,
        "roll_weight": 1.0,
        "purity_range": (0.92, 0.99),
        "blurb": "Heavenly lightning tempered your root in the womb.",
    },
    "Mutant Wind": {
        "rarity": "Legendary",
        "elements": ["Wind"],
        "absorption_multiplier": 3.2,
        "roll_weight": 0.75,
        "purity_range": (0.90, 0.98),
        "blurb": "Your Qi moves like a blade of invisible wind.",
    },
    "Mutant Ice": {
        "rarity": "Legendary",
        "elements": ["Ice"],
        "absorption_multiplier": 3.2,
        "roll_weight": 0.75,
        "purity_range": (0.90, 0.98),
        "blurb": "A frozen heart beats within a root of eternal frost.",
    },
    "Mutant Space": {
        "rarity": "Mythic",
        "elements": ["Space"],
        "absorption_multiplier": 4.0,
        "roll_weight": 0.25,
        "purity_range": (0.95, 0.99),
        "blurb": "Space itself bends toward your Dantian. Terrifying talent.",
    },
    "Divine Chaos": {
        "rarity": "Celestial",
        "elements": ["Chaos"],
        "absorption_multiplier": 6.0,
        "roll_weight": 0.2,
        "purity_range": (0.98, 1.0),
        "blurb": "Primordial Chaos before creation. The Dao whispers your name.",
    },
}

# ───────────────────────────────────────────────────────────────────
# BODY PHYSIQUES (Baoti) — rolled once at registration.
# dao_heart_guard: flat points subtracted from every Dao Heart loss.
# ───────────────────────────────────────────────────────────────────
PHYSIQUES = {
    "Mortal Flesh": {
        "tier": 0,
        "roll_weight": 87.9,
        "qi_absorption_bonus": 0.0,
        "tribulation_resistance": 0.0,
        "dao_heart_guard": 0.0,
        "blurb": "An ordinary vessel of flesh and blood.",
    },
    "Immortal Mortal Body": {
        "tier": 1,
        "roll_weight": 8.0,
        "qi_absorption_bonus": 0.10,
        "tribulation_resistance": 0.10,
        "dao_heart_guard": 5.0,
        "blurb": "It looks utterly ordinary... yet fate refuses to let it break.",
    },
    "Solar Divine Body": {
        "tier": 2,
        "roll_weight": 2.2,
        "qi_absorption_bonus": 0.20,
        "tribulation_resistance": 0.25,
        "dao_heart_guard": 10.0,
        "blurb": "A minor sun sleeps in your marrow. Fire and light obey you.",
    },
    "Nine Nether Yin Body": {
        "tier": 2,
        "roll_weight": 1.3,
        "qi_absorption_bonus": 0.20,
        "tribulation_resistance": 0.25,
        "dao_heart_guard": 10.0,
        "blurb": "Yin energy craves your body. Ghosts bow in your presence.",
    },
    "Ancient Sacred Body": {
        "tier": 3,
        "roll_weight": 0.6,
        "qi_absorption_bonus": 0.35,
        "tribulation_resistance": 0.40,
        "dao_heart_guard": 20.0,
        "blurb": "A body from the age of myths. Mountains crack against it.",
    },
}

# ───────────────────────────────────────────────────────────────────
# DAO HEART (Dao Xin) & KARMA — mental stability mechanics.
# ───────────────────────────────────────────────────────────────────
DAO_HEART = {
    "deviation_threshold": 30.0,          # Below this: Zou Huo Ru Mo risk
    "deviation_base_chance": 0.12,        # Per meditation, scaled by depth below threshold
    "deviation_qi_loss_ratio": 0.30,      # Qi lost on deviation episode
    "deviation_dao_heart_loss": 5.0,
    "deviation_karma_gain": 5.0,
    "success_recovery": 5.0,              # Dao Heart restored on breakthrough success
    "karma_sin_max": 1000,
}

# ───────────────────────────────────────────────────────────────────
# BREAKTHROUGH — attempt requirements, base odds, modifier scales.
# ───────────────────────────────────────────────────────────────────
BREAKTHROUGH = {
    "min_qi_ratio": 0.85,                 # Qi % required to attempt
    "standard_chance_mortal": 0.80,       # Realms 1-8, non-bottleneck
    "standard_chance_immortal": 0.60,     # Realms 9-15, non-bottleneck
    "bottleneck_chance_mortal": 0.55,     # Layer 3/6/9/Great Circle
    "bottleneck_chance_immortal": 0.40,   # Any 4-stage transition
    # (up_to_realm_inclusive, base_chance) — first matching row wins
    "realm_leap_base": [(3, 0.35), (8, 0.20), (12, 0.12), (16, 0.05)],
    # Modifier scales
    "fullness_bonus_scale": 0.50,         # Extra Qi above 85% → up to +7.5%
    "purity_bonus_scale": 0.20,           # Qi purity swing around midpoint
    "purity_midpoint": 0.50,
    "dao_heart_safe_zone": 80.0,          # No penalty above this stability
    "dao_heart_penalty_scale": 0.30,      # Max penalty at stability 0
    "meridian_penalty_scale": 0.25,       # Penalty at 100% meridian damage
    "insight_per_point": 0.05,            # Bottleneck comprehension scaling
    "insight_bonus_cap": 0.20,
    "chance_floor": 0.05,
    "chance_ceiling": 0.98,
    # On success
    "success_meridian_heal": 0.10,
    "success_dao_heart_gain": 5.0,
    "layer_advance_energy_pct": 0.15,     # Qi kept after layer advance (of OLD capacity)
    "realm_leap_energy_pct": 0.10,        # Qi kept after realm leap (of NEW capacity)
}

# Failure backlash table — weights are relative probabilities.
BACKLASH = [
    {
        "severity": "MINOR",
        "weight": 0.60,
        "qi_loss_ratio": 0.25,
        "meridian_damage": 0.05,
        "dao_heart_loss": 2.0,
        "stage_regression": False,
    },
    {
        "severity": "MODERATE",
        "weight": 0.30,
        "qi_loss_ratio": 0.50,
        "meridian_damage": 0.25,
        "dao_heart_loss": 10.0,
        "stage_regression": False,
    },
    {
        "severity": "CATASTROPHIC",
        "weight": 0.10,
        "qi_loss_ratio": 0.80,
        "meridian_damage": 0.50,
        "dao_heart_loss": 25.0,
        "stage_regression": True,
    },
]

# ───────────────────────────────────────────────────────────────────
# SOUL / PERMADEATH (Canhun) — death, possession, reincarnation.
# ───────────────────────────────────────────────────────────────────
SOUL = {
    "remnant_min_realm": 4,               # Nascent Soul and above survive as Remnant Souls
    "vitality_decay_per_hour": 4.0,       # Remnant Soul timer (100 → ~25h to find a vessel)
    "body_destroyed_on_total_rupture": True,  # Catastrophic backlash at 100% meridian damage kills
    # Possession (Duo She)
    "possession_base_chance": 0.45,
    "possession_vitality_bonus_scale": 0.003,   # ×current vitality (100 → +30%)
    "possession_strength_penalty": 0.04,        # ×target strength (10 → -40%)
    "possession_success_karma": 40,             # Heaven marks this sin
    "possession_fail_karma": 10,
    "possession_fail_vitality_cost": 25.0,
    # Karmic Legacy awarded on TRUE DEATH
    "legacy_base": 2,
    "legacy_per_realm": 5,                # × (highest_realm - 1)
    "legacy_per_breakthrough_win": 1,
    # Reincarnation — tokens are spent for the new life
    "reincarnation_luck_per_token": 0.004,      # Rare-root weight shift per token
    "reincarnation_luck_cap": 0.35,
    "reincarnation_stones_per_token": 2,        # Starting spirit stone bonus
    "reincarnation_stones_cap": 400,
    "reincarnation_comprehension_retention": 0.10,  # % of past-life insight carried over
}

# ───────────────────────────────────────────────────────────────────
# ENGAGEMENT PSYCHOLOGY — streaks, near-miss, variable rewards.
# ───────────────────────────────────────────────────────────────────
ENGAGEMENT = {
    # Daily meditation streak: (min_streak_days, qi_multiplier)
    "streak_multipliers": [(3, 1.10), (7, 1.25), (14, 1.50), (30, 2.00)],
    # Near-miss: failed roll within this distance of the required chance
    "near_miss_threshold": 0.06,
    "near_miss_consolation_insight": 1,   # Dao Insight granted on near-miss (sunk-cost keeper)
    # Variable-ratio windfalls on meditation (jackpot feeling)
    "windfall_chance": 0.08,
    "windfall_insight_range": (1, 6),
    "windfall_stone_chance": 0.03,        # Bonus roll on top of insight windfall
    "windfall_stone_range": (5, 25),
    # Realm milestone titles (auto-applied while title is not custom)
    "default_title": "Wandering Cultivator",
    "realm_titles": {
        2: "Foundation Seeker",
        3: "Golden Core Sovereign",
        4: "Nascent Soul Monarch",
        5: "Divine Transcendent",
        6: "Void Walker",
        7: "Integration Saint",
        8: "Tribulation Overlord",
        9: "True Immortal",
        10: "Golden Immortal",
        11: "Taiyi Sovereign",
        12: "Daluo Eternal",
        13: "Dao Ancestor",
        14: "Chaos Saint",
        15: "Creation God",
        16: "Eternal Transcendent",
    },
}


# ───────────────────────────────────────────────────────────────────
# LUCK STAT — a cultivator-wide stat (User.luck_stat).
# Feeds windfalls, gathering rarity, crafting coincidences.
# ───────────────────────────────────────────────────────────────────
LUCK = {
    "starting_luck": 5,
    "max_luck": 100,
    "windfall_chance_per_point": 0.002,     # × luck added to ENGAGEMENT windfall chance
    "gather_rare_shift_per_point": 0.15,    # % shift toward older herbs/rarer ores
    "alchemy_coincidence_per_point": 0.004, # see ALCHEMY below
}

# ───────────────────────────────────────────────────────────────────
# GATHERING (placeholder forager until v0.4 world engine lands).
# ───────────────────────────────────────────────────────────────────
GATHERING = {
    "cooldown_minutes": 30,
    "herb_chance": 0.55,
    "mineral_chance": 0.30,               # else: nothing found this trip
    # Age-tier base weights for herbs; realm multiplies each tier's weight
    "age_tier_weights_base": [55, 28, 13, 4],
    "age_tier_realm_scaling": [1.0, 1.02, 1.05, 1.08],  # weight *= factor^(realm-1)
}

HERB_ELEMENTS = ["Metal", "Wood", "Water", "Fire", "Earth"]
HERB_ELEMENT_NAMES = {
    "Metal": "Golden-Leaf Grass",
    "Wood": "Verdant Spirit Vine",
    "Water": "Moonwell Lotus",
    "Fire": "Crimson Flame Blossom",
    "Earth": "Yellow Dragon Root",
}
# age_years: (id_suffix, potency_mult, gather_weight, price)
HERB_AGES = [
    (100, "100", 1.0, 55.0, 20),
    (500, "500", 1.9, 28.0, 65),
    (1000, "1000", 3.4, 13.0, 170),
    (10000, "10000", 7.5, 4.0, 650),
]
# Composed registry: herb_<element>_<age>
HERBS = {}
for _el in HERB_ELEMENTS:
    for _age, _suf, _pot, _w, _price in HERB_AGES:
        HERBS[f"herb_{_el.lower()}_{_age}"] = {
            "id": f"herb_{_el.lower()}_{_age}",
            "name": f"{HERB_ELEMENT_NAMES[_el]} ({_age}-Year)",
            "category": "Herb",
            "element": _el,
            "age_years": _age,
            "potency": round(10.0 * _pot, 1),
            "gather_weight": _w,
            "base_price": _price,
        }

MINERALS = {
    "ore_iron": {"name": "Black Iron Ore", "category": "Mineral", "tier": 1, "forge_power": 10, "gather_weight": 30, "base_price": 15},
    "ore_cold_iron": {"name": "Cold Iron Ore", "category": "Mineral", "tier": 2, "forge_power": 25, "gather_weight": 20, "base_price": 40},
    "ore_purple_copper": {"name": "Purple Copper", "category": "Mineral", "tier": 2, "forge_power": 32, "gather_weight": 15, "base_price": 60},
    "ore_mystic_silver": {"name": "Mystic Silver", "category": "Mineral", "tier": 3, "forge_power": 60, "gather_weight": 8, "base_price": 150},
    "ore_star_core_iron": {"name": "Star-Core Iron", "category": "Mineral", "tier": 4, "forge_power": 120, "gather_weight": 4, "base_price": 400},
    "ore_void_source": {"name": "Void-Source Crystal", "category": "Mineral", "tier": 5, "forge_power": 260, "gather_weight": 1.5, "base_price": 1200},
}

FURNACES = {
    "furnace_mortal_iron": {"name": "Mortal Iron Furnace", "tier": 1, "impurity_reduction": 0.0, "success_bonus": 0.00, "base_price": 0},
    "furnace_earth_vein": {"name": "Earth-Vein Cauldron", "tier": 2, "impurity_reduction": 6.0, "success_bonus": 0.03, "base_price": 800},
    "furnace_heaven_burner": {"name": "Heaven-Burner Furnace", "tier": 3, "impurity_reduction": 12.0, "success_bonus": 0.06, "base_price": 3500},
    "furnace_primordial_chaos": {"name": "Primordial Chaos Cauldron", "tier": 4, "impurity_reduction": 20.0, "success_bonus": 0.10, "base_price": 12000},
}

FLAMES = {
    "flame_wood": {"name": "Woodkindled Flame", "impurity_reduction": 2.0, "base_price": 10},
    "flame_earth_core": {"name": "Earth-Core Earthfire", "impurity_reduction": 5.0, "base_price": 45},
    "flame_celestial_spirit": {"name": "Celestial Spirit Flame", "impurity_reduction": 9.0, "base_price": 160},
}

# ───────────────────────────────────────────────────────────────────
# PILL RECIPES (*Dan Dao*) — tiered by cultivation realm.
# Effects are multiplied by the pill's quality-grade potency.
# NOTE: numbers are first-pass seeds — re-tune after playtesting/research.
# ───────────────────────────────────────────────────────────────────
PILL_RECIPES = {
    "qi_gathering_pill": {
        "name": "Qi Gathering Pill",
        "tier": 1, "min_realm": 1, "alchemy_level_req": 1,
        "base_impurity": 38.0,
        "materials": {"herb_wood_100": 2, "herb_water_100": 1},
        "effects": {"qi_amount": 40.0},
        "xp_reward": 20, "base_price": 60,
        "blurb": "A humble pill that floods the meridians with gathered Qi.",
    },
    "marrow_cleansing_pill": {
        "name": "Marrow Cleansing Pill",
        "tier": 1, "min_realm": 1, "alchemy_level_req": 2,
        "base_impurity": 42.0,
        "materials": {"herb_metal_500": 1, "herb_earth_100": 2},
        "effects": {"toxicity_cleanse": 35.0},
        "xp_reward": 25, "base_price": 90,
        "blurb": "Scours accumulated pill toxins from marrow and organs.",
    },
    "nine_turn_soul_pill": {
        "name": "Nine-Turn Soul Replenishing Pill",
        "tier": 2, "min_realm": 2, "alchemy_level_req": 3,
        "base_impurity": 48.0,
        "materials": {"herb_water_1000": 1, "herb_wood_500": 2},
        "effects": {"dao_heart_restore": 25.0},
        "xp_reward": 40, "base_price": 200,
        "blurb": "Mends a shattered Dao Heart and stills inner demons.",
    },
    "foundation_establishment_pill": {
        "name": "Foundation Establishment Pill",
        "tier": 2, "min_realm": 2, "alchemy_level_req": 3,
        "base_impurity": 50.0,
        "materials": {"herb_fire_500": 2, "herb_wood_500": 2},
        "effects": {"breakthrough_bonus": 0.15},
        "xp_reward": 45, "base_price": 220,
        "blurb": "Grants a surge of insight before attempting a Foundation breakthrough.",
    },
    "life_extension_pill": {
        "name": "Life-Extending Rejuvenation Pill",
        "tier": 3, "min_realm": 3, "alchemy_level_req": 5,
        "base_impurity": 55.0,
        "materials": {"herb_wood_1000": 2, "herb_earth_1000": 1},
        "effects": {"lifespan_years": 50.0},
        "xp_reward": 70, "base_price": 480,
        "blurb": "Winds back the clock of flesh. Time itself hesitates.",
    },
    "core_condensation_pill": {
        "name": "Core Condensation Pill",
        "tier": 3, "min_realm": 3, "alchemy_level_req": 6,
        "base_impurity": 58.0,
        "materials": {"herb_fire_1000": 2, "herb_metal_1000": 1},
        "effects": {"breakthrough_bonus": 0.18},
        "xp_reward": 85, "base_price": 550,
        "blurb": "Aids the perilous shattering into the Golden Core realm.",
    },
    "nascent_soul_formation_pill": {
        "name": "Nascent Soul Formation Pill",
        "tier": 4, "min_realm": 4, "alchemy_level_req": 8,
        "base_impurity": 68.0,
        "materials": {"herb_water_10000": 1, "herb_fire_10000": 1, "herb_wood_10000": 1},
        "effects": {"breakthrough_bonus": 0.25},
        "xp_reward": 150, "base_price": 1500,
        "blurb": "The cradle of a Nascent Soul. Legends are brewed here.",
    },
    "tribulation_shield_pill": {
        "name": "Tribulation Shield Pill",
        "tier": 3, "min_realm": 3, "alchemy_level_req": 6,
        "base_impurity": 52.0,
        "materials": {"herb_metal_1000": 2, "ore_mystic_silver": 1},
        "effects": {"tribulation_shield": 60.0},
        "xp_reward": 80, "base_price": 420,
        "blurb": "Swallow before the storm: a ward of pure metal-Qi against heavenly lightning.",
    },
    "heaven_defying_rebirth_pill": {
        "name": "Heaven-Defying Rebirth Pill",
        "tier": 5, "min_realm": 5, "alchemy_level_req": 9,
        "base_impurity": 75.0,
        "materials": {"herb_fire_10000": 1, "herb_water_10000": 1, "herb_metal_10000": 1},
        "effects": {"vitality_restore": 100.0},
        "xp_reward": 250, "base_price": 3000,
        "blurb": "Reforges a dissolving Remnant Soul. Death itself is refused entry.",
    },
}

# ───────────────────────────────────────────────────────────────────
# ARTIFACTS (*Qi Dao*) — 4 equip slots × 5 tiers, composed below.
# passive_qi_bonus applies immediately during meditation;
# tribulation_resistance & power are consumed by the v0.4 engines.
# ───────────────────────────────────────────────────────────────────
ARTIFACT_SLOTS = {
    "weapon": {"label": "Flying Sword", "names": ["Ironwhisper Sword", "Azure River Sword", "Ninefold Thunder Blade", "Star-Severing Sword", "Primordial Heaven-Cleaver"]},
    "armor": {"label": "Defensive Armor", "names": ["Turtleweave Robe", "Jade-Scale Cuirass", "Mountain-Bearer Plate", "Dragonbone Warplate", "Chaos-Aegis Regalia"]},
    "banner": {"label": "Spirit Banner", "names": ["Gathering Mist Banner", "Five-Element Banner", "Soul-Guiding Banner", "Void-Drawing Banner", "Genesis Unfurling Banner"]},
    "rod": {"label": "Lightning Rod", "names": ["Copper Bell Rod", "Storm-Grounding Rod", "Thunder-Diverting Rod", "Nine-Heaven Lightning Rod", "Eternal Calamity Rod"]},
}
ARTIFACT_TIERS = [
    # (tier_name, qi_bonus, trib_resistance, power, forging_level_req, material_costs)
    ("mortal", 0.02, 0.03, 10, 1, {"ore_iron": 3}),
    ("magical", 0.05, 0.08, 40, 3, {"ore_cold_iron": 2, "ore_purple_copper": 2}),
    ("spirit", 0.09, 0.15, 140, 5, {"ore_mystic_silver": 3, "ore_cold_iron": 4}),
    ("dao", 0.14, 0.24, 480, 7, {"ore_star_core_iron": 3, "ore_mystic_silver": 4}),
    ("primordial", 0.20, 0.36, 1500, 9, {"ore_void_source": 2, "ore_star_core_iron": 5}),
]
ARTIFACTS = {}
for _slot, _cfg in ARTIFACT_SLOTS.items():
    for _i, (_tname, _qi, _trib, _pow, _lvl, _mats) in enumerate(ARTIFACT_TIERS):
        ARTIFACTS[f"{_slot}_{_tname}"] = {
            "id": f"{_slot}_{_tname}",
            "name": f"{_cfg['names'][_i]}",
            "category": "Artifact",
            "slot": _slot,
            "tier": _tname,
            "passive_qi_bonus": _qi if _slot != "rod" else _qi * 0.5,
            "tribulation_resistance": _trib,
            "power": _pow,
            "forging_level_req": _lvl,
            "materials": _mats,
        }

def _artifact_base_price(tier_index: int) -> int:
    return [80, 320, 1100, 3600, 12000][tier_index]

for _key, _art in ARTIFACTS.items():
    _art["base_price"] = _artifact_base_price([t[0] for t in ARTIFACT_TIERS].index(_art["tier"]))

# ───────────────────────────────────────────────────────────────────
# ALCHEMY TUNING — quality is EARNED through mastery, not pure luck.
# Every brew yields an IMPURITY value [0,100]; lower = better grade:
#   FLAWLESS < 1.0 | TOP <= 10 | MEDIUM <= 32 | LOW > 32
# Mastery lowers the center AND narrows the random spread (consistency).
# Luck only triggers occasional "heavenly coincidences" toward purity.
# Toxicity comes from residual impurities — Flawless is toxin-free.
# ───────────────────────────────────────────────────────────────────
ALCHEMY = {
    "grade_thresholds": {"top_max": 10.0, "medium_max": 32.0},   # flawless < 1.0 hard floor below
    "flawless_hard_max": 1.0,
    # Impurity roll model: gaussian(center, spread)
    "mastery_control_per_level": 2.2,      # center lowered per alchemy level
    "spread_base": 14.0,
    "spread_shrink_per_level": 1.1,
    "spread_min": 3.0,
    # Heavenly Coincidence (the ONLY path where luck bends purity)
    "coincidence_base_chance": 0.02,
    "coincidence_per_luck": 0.004,         # luck 5 → 4% | luck 50 → 22%
    "coincidence_impurity_factor": 0.12,   # dramatic drop when it fires
    # Nominal impurity per grade (used for consumption toxicity of stacked pills)
    "grade_nominal_impurity": {"Low": 45.0, "Medium": 20.0, "Top": 6.0, "Flawless": 0.0},
    "toxicity_per_impurity_point": 0.7,    # consumption toxicity build-up
    "pill_toxicity_cap": 100.0,
    # Toxicity penalties while toxic
    "absorption_stall_scale": 0.6,         # at 100 toxicity → 60% slower Qi gain
    "breakthrough_penalty_scale": 0.15,    # at 100 toxicity → -15% success odds
    "natural_decay_per_meditation": 0.5,   # slow cleanse by simply cultivating
    # Quality-grade potency multipliers applied to recipe effects
    "grade_potency": {"Low": 0.70, "Medium": 1.00, "Top": 1.35, "Flawless": 1.75},
    "grade_xp_bonus": {"Low": 1.0, "Medium": 1.25, "Top": 1.6, "Flawless": 2.5},
    # Stored breakthrough bonus from booster pills (applied to next attempt)
    "max_stored_breakthrough_bonus": 0.40,
    # Mastery progression
    "level_titles": ["Novice", "Apprentice", "Adept", "Alchemist", "Senior Alchemist",
                     "Pill Master", "Grand Pill Master", "Pill King", "Pill Emperor", "Pill Sovereign"],
    "xp_curve": [0, 80, 200, 420, 760, 1250, 2000, 3100, 4700, 7000],
}

FORGING = {
    "success_base_by_tier": {"mortal": 0.90, "magical": 0.75, "spirit": 0.55, "dao": 0.35, "primordial": 0.18},
    "success_per_level": 0.02,
    "success_cap": 0.95,
    "fail_material_loss_ratio": 0.5,       # half of each material lost on failure
    "fail_xp_ratio": 0.4,
    "xp_by_tier": {"mortal": 15, "magical": 35, "spirit": 70, "dao": 130, "primordial": 240},
    "level_titles": ["Novice Smith", "Apprentice Smith", "Artisan", "Forgemaster", "Senior Forgemaster",
                     "Treasure Refiner", "Grand Refiner", "Artifact King", "Artifact Emperor", "Qi Dao Sovereign"],
    "xp_curve": [0, 90, 220, 460, 840, 1380, 2200, 3400, 5100, 7500],
}

# ───────────────────────────────────────────────────────────────────
# SPIRIT STONE ECONOMY — wallet column holds LOW-grade stones;
# Mid/High/Top grades live in inventory as currency items (100:1).
# ───────────────────────────────────────────────────────────────────
ECONOMY = {
    "conversion_ratio": 100,
    "buy_markup": 1.25,
    "sell_ratio": 0.45,
    "currency_items": {
        "mid_grade_stones": {"name": "Mid-Grade Spirit Stones", "low_equivalent": 100, "base_price": 125},
        "high_grade_stones": {"name": "High-Grade Spirit Stones", "low_equivalent": 10000, "base_price": 12500},
        "top_grade_stones": {"name": "Top-Grade Spirit Stones", "low_equivalent": 1000000, "base_price": 1250000},
    },
    "merchant_daily_slots": 6,
    "merchant_sell_grade_mult": {"Low": 0.8, "Medium": 1.0, "Top": 1.3, "Flawless": 1.7},
}

MERCHANT_STOCK_POOL = [
    {"item_id": "flame_wood", "weight": 20, "min_realm": 1},
    {"item_id": "flame_earth_core", "weight": 10, "min_realm": 1},
    {"item_id": "flame_celestial_spirit", "weight": 4, "min_realm": 2},
    {"item_id": "furnace_earth_vein", "weight": 3, "min_realm": 1},
    {"item_id": "furnace_heaven_burner", "weight": 1, "min_realm": 2},
    {"item_id": "herb_fire_500", "weight": 8, "min_realm": 1},
    {"item_id": "herb_water_500", "weight": 8, "min_realm": 1},
    {"item_id": "herb_metal_1000", "weight": 5, "min_realm": 2},
    {"item_id": "herb_wood_1000", "weight": 5, "min_realm": 2},
    {"item_id": "herb_earth_1000", "weight": 5, "min_realm": 2},
    {"item_id": "herb_fire_10000", "weight": 1, "min_realm": 3},
    {"item_id": "herb_water_10000", "weight": 1, "min_realm": 3},
    {"item_id": "herb_wood_10000", "weight": 1, "min_realm": 3},
    {"item_id": "herb_metal_10000", "weight": 1, "min_realm": 3},
    {"item_id": "herb_earth_10000", "weight": 1, "min_realm": 3},
    {"item_id": "ore_cold_iron", "weight": 8, "min_realm": 1},
    {"item_id": "ore_purple_copper", "weight": 6, "min_realm": 1},
    {"item_id": "ore_mystic_silver", "weight": 4, "min_realm": 2},
    {"item_id": "ore_star_core_iron", "weight": 2, "min_realm": 3},
    {"item_id": "ore_void_source", "weight": 0.5, "min_realm": 4},
]

# Every registry entry carries its own id (self-keying for UI/serialization)
for _reg in (HERBS, MINERALS, FURNACES, FLAMES):
    for _key, _val in _reg.items():
        _val.setdefault("id", _key)

# ───────────────────────────────────────────────────────────────────
# HEAVENLY TRIBULATIONS (*Tianjie*) — mandatory for major realm
# crossings into Realm >= min_target_realm. Interactive: one action
# per wave (endure / sacrifice artifact / shield pill / bail).
# Pools model: stored Qi absorbs first, then body integrity; gear and
# physique resist physical waves; spiritual lightning ignores gear.
# ───────────────────────────────────────────────────────────────────
TRIBULATION = {
    "min_target_realm": 4,               # Leaps INTO realm 4+ trigger the storm
    # Strike-count tiers (Four-Nine / Six-Nine / Nine-Nine)
    "tier_strikes": {"FOUR_NINE": 36, "SIX_NINE": 54, "NINE_NINE": 81},
    "six_nine_karma": 300,               # karma_sin >= this → heavens angrier
    "nine_nine_karma": 600,
    "six_nine_root_rarities": ["Epic", "Legendary"],
    "nine_nine_roots": ["Divine Chaos", "Mutant Space"],   # heaven-defying talent
    # Baseline strike damage by TARGET realm (tunable difficulty spine)
    "base_strike_damage": {
        4: 40, 5: 55, 6: 75, 7: 100, 8: 135,
        9: 180, 10: 240, 11: 320, 12: 430, 13: 570, 14: 760, 15: 1000, 16: 1300,
    },
    "wave_multiplier": {1: 1.0, 2: 1.4, 3: 1.8, 4: 2.2},   # W factor from roadmap formula
    "strike_escalation": 0.08,           # per-strike growth within a wave (b factor)
    "t_score_exponent": 1.35,            # heaven-intensity curve across realms (roadmap formula)
    # Wave composition — ratios of total strikes per wave
    "waves": [
        {"wave": 1, "type": "PHYSICAL", "strikes_ratio": 0.30},
        {"wave": 2, "type": "PHYSICAL", "strikes_ratio": 0.30},
        {"wave": 3, "type": "SPIRITUAL", "strikes_ratio": 0.25},
        {"wave": 4, "type": "HEART_DEMON", "strikes_ratio": 0.15},
    ],
    # Player power composite (T_score) — defense scales damage DOWN via ratio below
    "t_score": {
        "realm_weight": 10.0,
        "stage_index_weight": 3.0,       # × stage position within realm
        "artifact_power_divisor": 10.0,  # equipped artifact power summed / divisor
        "physique_tier_weight": 8.0,
        "luck_weight": 0.5,
    },
    "defense_ratio_cap": 0.80,           # max fraction of strike damage mitigated by power
    "defense_softener": 60.0,            # higher = power mitigates less (mitig = cap·T/(T+softener))
    "physique_resistance_scale": 0.35,   # tribulation_resistance 0.4 → -14% phys wave dmg
    "artifact_absorb_efficiency": 0.9,   # gear soaks damage at this efficiency before breaking
    "sacrifice_absorbs_full_wave": True, # destroying an artifact nullifies the whole next wave
    # Body/Qi pools
    "body_pool_factor": 0.6,             # body integrity = max_energy × this on entry
    "meridian_scar_per_body_point": 0.0004,  # body pool loss → permanent meridian damage
    "death_meridian_threshold": 1.0,     # meridian damage at/above this = body destroyed
    # Heart-demon wave (Wave 4): contested willpower check per burst
    "heart_demon_bursts": 3,
    "illusion_power_base": 45.0,
    "illusion_power_per_target_realm": 6.0,
    "illusion_power_per_100_sin": 18.0,
    "willpower_from_dao_heart": 1.0,
    "willpower_luck_weight": 0.8,
    "dao_heart_loss_per_burst_fail": 22.0,
    # Bail out ("turning back from the storm")
    "bail_meridian_penalty": 0.35,
    "bail_dao_heart_loss": 20.0,
    "bail_karma_gain": 20,
    # Rewards
    "survive_dao_heart_gain": 10.0,
}

# ───────────────────────────────────────────────────────────────────
# OPEN WORLD (*Tianxia*) — node graph. Seeded into world_nodes table
# at startup; edit here, restart, world updates itself.
# ───────────────────────────────────────────────────────────────────
WORLD = {
    "starting_node": "sect_valley",
    "travel_cooldown_base_minutes": 5.0,     # + scaled by destination danger
    "travel_cooldown_per_danger": 1.5,
    "travel_qi_cost_pct": 0.05,              # of max_energy per trip
    "explore_cooldown_minutes": 20.0,        # replaces old GATHERING cooldown
    "elemental_bias_boost": 0.35,            # matching-root meditation bonus
}

WORLD_NODES = {
    # ── Central hub ──
    "sect_valley": {
        "name": "Central Heavenly Sect Valley", "region": "Central Valley",
        "plane": "Mortal Domain", "spirit_density": 2.0, "elemental_bias": "Balanced",
        "danger_tier": 1, "connections": ["azure_river_dock", "crimson_oasis", "frostpine_pass", "demon_ridge_gate", "spirit_realm_gate"],
        "description": "Ten thousand stone steps ringed by floating pavilions. The safest Qi under heaven.",
    },
    # ── Eastern Sea Archipelago (Water/Wood) ──
    "azure_river_dock": {
        "name": "Azure River Dock", "region": "Eastern Sea Archipelago",
        "plane": "Mortal Domain", "spirit_density": 1.5, "elemental_bias": "Water",
        "danger_tier": 2, "connections": ["sect_valley", "pearl_atoll"],
        "description": "Salt-wind junks and fishermen's shrines. Moonwell Lotuses grow along the pilings.",
    },
    "pearl_atoll": {
        "name": "Pearl Atoll", "region": "Eastern Sea Archipelago",
        "plane": "Mortal Domain", "spirit_density": 2.5, "elemental_bias": "Water",
        "danger_tier": 4, "connections": ["azure_river_dock", "sunken_ruin_shoals"],
        "description": "A drowned coral crown where tide-spirits barter pearls for poems.",
    },
    "sunken_ruin_shoals": {
        "name": "Sunken Ruin Shoals", "region": "Eastern Sea Archipelago",
        "plane": "Mortal Domain", "spirit_density": 3.5, "elemental_bias": "Water",
        "danger_tier": 7, "connections": ["pearl_atoll"],
        "description": "An Immortal-era harbor lies beneath green water. Things still patrol its streets.",
    },
    # ── Southern Crimson Desert (Fire/Earth) ──
    "crimson_oasis": {
        "name": "Crimson Oasis", "region": "Southern Crimson Desert",
        "plane": "Mortal Domain", "spirit_density": 1.6, "elemental_bias": "Fire",
        "danger_tier": 2, "connections": ["sect_valley", "glass_dunes"],
        "description": "A spring-fed ring of palms where caravan masters water their sand-lizards.",
    },
    "glass_dunes": {
        "name": "Glass Dunes", "region": "Southern Crimson Desert",
        "plane": "Mortal Domain", "spirit_density": 2.8, "elemental_bias": "Fire",
        "danger_tier": 5, "connections": ["crimson_oasis", "volcanic_crown"],
        "description": "Lightning-fused sand sings underfoot. Purple Copper veins glitter at dusk.",
    },
    "volcanic_crown": {
        "name": "Volcanic Crown", "region": "Southern Crimson Desert",
        "plane": "Mortal Domain", "spirit_density": 4.5, "elemental_bias": "Fire",
        "danger_tier": 8, "connections": ["glass_dunes"],
        "description": "The mountain wears a lake of fire. Ten-thousand-year herbs bloom on its rim.",
    },
    # ── Northern Ice Abyss (Metal/Water) ──
    "frostpine_pass": {
        "name": "Frostpine Pass", "region": "Northern Ice Abyss",
        "plane": "Mortal Domain", "spirit_density": 1.7, "elemental_bias": "Metal",
        "danger_tier": 3, "connections": ["sect_valley", "glacier_mirror"],
        "description": "Wind-carved pines and iron-hard frost. Cold Iron litters the scree.",
    },
    "glacier_mirror": {
        "name": "Glacier Mirror", "region": "Northern Ice Abyss",
        "plane": "Mortal Domain", "spirit_density": 3.2, "elemental_bias": "Ice",
        "danger_tier": 6, "connections": ["frostpine_pass", "abyssal_rift"],
        "description": "A frozen lake so clear it reflects other skies. Do not trust the reflections.",
    },
    "abyssal_rift": {
        "name": "Abyssal Rift", "region": "Northern Ice Abyss",
        "plane": "Mortal Domain", "spirit_density": 5.5, "elemental_bias": "Space",
        "danger_tier": 10, "connections": ["glacier_mirror"],
        "description": "A wound in the world humming with Void-Source echoes. Cultivators vanish here.",
    },
    # ── Western Demon Ridge (Demonic) ──
    "demon_ridge_gate": {
        "name": "Demon Ridge Gate", "region": "Western Demon Ridge",
        "plane": "Mortal Domain", "spirit_density": 1.8, "elemental_bias": "Earth",
        "danger_tier": 3, "connections": ["sect_valley", "bone_forest"],
        "description": "A pass marked by nine weathered skull-totems. Travelers leave offerings.",
    },
    "bone_forest": {
        "name": "Bone Forest", "region": "Western Demon Ridge",
        "plane": "Mortal Domain", "spirit_density": 3.0, "elemental_bias": "Wood",
        "danger_tier": 7, "connections": ["demon_ridge_gate", "blood_altar_peaks"],
        "description": "White trees grown through older, paler things. The Yin energy is thick as broth.",
    },
    "blood_altar_peaks": {
        "name": "Blood Altar Peaks", "region": "Western Demon Ridge",
        "plane": "Mortal Domain", "spirit_density": 6.0, "elemental_bias": "Chaos",
        "danger_tier": 12, "connections": ["bone_forest"],
        "description": "Where demonic dao lords once butchered a generation. Rich beyond reason; lethal beyond mercy.",
    },
    # ── Spirit Realm Gate ──
    "spirit_realm_gate": {
        "name": "Spirit Realm Gate", "region": "Central Valley",
        "plane": "Spirit Realm", "spirit_density": 8.0, "elemental_bias": "Balanced",
        "danger_tier": 14, "connections": ["sect_valley"],
        "description": "A shimmering arch left by ascended masters. Mortal flesh aches just to approach.",
    },
}

# Encounter roll table for exploration — weights shift with node danger.
ENCOUNTERS = {
    "herb_find": {"base_weight": 30, "danger_scaling": -1.5},
    "mineral_vein": {"base_weight": 22, "danger_scaling": 0.5},
    "wandering_caravan": {"base_weight": 12, "danger_scaling": 0.0},
    "ancient_cave": {"base_weight": 10, "danger_scaling": 1.2},
    "ambush": {"base_weight": 14, "danger_scaling": 2.0},
    "nothing": {"base_weight": 12, "danger_scaling": -0.5},
}
ENCOUNTER_TUNING = {
    "herb_age_danger_bonus": 0.5,          # higher danger → older herbs likelier
    "caravan_stock_slots": 3,
    # Ancient cave gamble
    "cave_success_chance_base": 0.55,
    "cave_reward_insight_range": (2, 8),
    "cave_reward_stones_range": (50, 400),
    "cave_reward_herb_age_min": 1000,      # legacy herbs on success
    "cave_trap_meridian_damage": (0.05, 0.20),
    "cave_trap_qi_loss_ratio": 0.4,
    # Ambush clash
    "player_realm_weight": 10.0,
    "player_stage_weight": 3.0,
    "player_artifact_divisor": 10.0,
    "player_physique_weight": 8.0,
    "player_luck_weight": 0.5,
    "enemy_power_per_danger": 9.0,
    "enemy_variance": (0.8, 1.3),
    "win_loot_stones_range": (20, 200),
    "loss_meridian_damage_range": (0.04, 0.15),
    "loss_stone_loss_ratio": 0.25,
    "flee_base_chance": 0.55,
    "flee_per_luck": 0.008,
    "flee_per_danger_penalty": 0.03,
}


# ───────────────────────────────────────────────────────────────────
# NARRATION — "The Heavenly Dao" persona. Provider chain lives in
# .env (NARRATION_PROVIDERS + keys); the VOICE lives here.
# Templates use str.format(**context) with profile fields.
# ───────────────────────────────────────────────────────────────────
NARRATION = {
    "persona_name": "The Heavenly Dao",
    "system_prompt": (
        "You are The Heavenly Dao — the impersonal yet oddly attentive voice of heaven "
        "in a xianxia cultivation world. You narrate cultivators' deeds in flowing, "
        "slightly archaic prose: grand for triumphs, coldly amused at folly, mournful at death. "
        "Address the cultivator in second person ('you'). Keep it under 120 words. "
        "Never break character, never mention being an AI, never use modern slang."
    ),
    "temperature": 0.9,
    "max_tokens": 300,
    # Event templates: {placeholders} filled from the cultivator's live profile
    "event_templates": {
        "breakthrough": (
            "The cultivator {username} has just shattered through to {realm_name_en} ({stage})! "
            "Their Dao title is now '{dao_title}'. Speak of this ascension."
        ),
        "tribulation_summoned": (
            "{username} dared to cross into Realm {target_realm} — and heaven answered with a "
            "{tier} Tribulation of {total_strikes} lightning strikes. Set the scene of the gathering storm."
        ),
        "tribulation_survived": (
            "{username} endured {strikes_endured} heavenly strikes and stepped into Realm {realm_advanced_to} "
            "as a {dao_title}. Proclaim their survival across the nine skies."
        ),
        "tribulation_destroyed": (
            "{username}'s body was obliterated by heavenly lightning after enduring {strikes_endured} strikes. "
            "Yet a nascent soul escaped the ruin. Mourn the flesh; hint at what lingers."
        ),
        "true_death": (
            "{username} has died a true death at {realm_name_en}. Their karma passes on as legacy. "
            "Eulogize them as only heaven can — indifferent, yet not unkind."
        ),
        "windfall": (
            "Mid-meditation, {username} received an epiphany: {windfall_message} Remark on fortune's whimsy."
        ),
        "reincarnation": (
            "{username} has reincarnated into Generation {lineage_generation}, born anew with "
            "{spiritual_root} roots and {physique_name}. Speak of the wheel turning."
        ),
        "possession": (
            "{username}, a bodiless remnant soul, has seized a mortal vessel named {target_name}. "
            "Narrate this profane act and heaven's disapproval."
        ),
    },
    # Used when NO provider key is configured or all providers fail — game keeps working
    "fallback_lines": {
        "breakthrough": "The Dao trembles faintly... somewhere, a barrier shatters.",
        "tribulation_summoned": "Clouds gather where no clouds should be.",
        "tribulation_survived": "The storm parts. Someone below still breathes.",
        "tribulation_destroyed": "Ash drifts on a wind that remembers a name.",
        "true_death": "A star gutters out beyond the ninth heaven.",
        "windfall": "Fortune is a fickle master.",
        "reincarnation": "The wheel turns; a new life stirs.",
        "possession": "An old sin wears new skin tonight.",
    },
}


def get_root_config(root_name: str) -> dict:
    return ROOTS.get(root_name, ROOTS["Mortal Five-Element"])


def get_physique_config(physique_name: str) -> dict:
    return PHYSIQUES.get(physique_name, PHYSIQUES["Mortal Flesh"])


# ───────────────────────────────────────────────────────────────────
# UNIFIED ITEM REGISTRY — every ownable/tradeable thing, one lookup.
# ───────────────────────────────────────────────────────────────────
ITEMS_REGISTRY: Dict[str, Dict[str, Any]] = {}
ITEMS_REGISTRY.update(HERBS)
ITEMS_REGISTRY.update(MINERALS)
ITEMS_REGISTRY.update(FURNACES)
ITEMS_REGISTRY.update(FLAMES)
ITEMS_REGISTRY.update(ARTIFACTS)
for _cid, _cdef in ECONOMY["currency_items"].items():
    ITEMS_REGISTRY[_cid] = {"id": _cid, "name": _cdef["name"], "category": "Currency", "base_price": _cdef["base_price"]}
for _pid, _r in PILL_RECIPES.items():
    ITEMS_REGISTRY[_pid] = {
        "id": _pid, "name": _r["name"], "category": "Pill",
        "tier": _r["tier"], "min_realm": _r["min_realm"], "base_price": _r["base_price"],
    }


def get_item(item_id: str) -> Optional[Dict[str, Any]]:
    return ITEMS_REGISTRY.get(item_id)
