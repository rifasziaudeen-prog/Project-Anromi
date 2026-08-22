"""
World Engine (*Tianxia*) — node graph travel, exploration encounters,
ancient cave gambles, and lightweight ambush clashes.
Pure math only; routes apply DB side-effects.
All tunables in core/balance.py → WORLD / ENCOUNTERS / ENCOUNTER_TUNING.
"""
import random
from typing import Dict, Any, Optional, List, Tuple

from core.balance import (
    WORLD, WORLD_NODES, ENCOUNTERS, ENCOUNTER_TUNING,
    HERBS, MINERALS,
)
from services.gathering_engine import _age_tier_weights


# ── Graph helpers ────────────────────────────────────────────────────

def get_node(node_id: str) -> Optional[Dict[str, Any]]:
    return WORLD_NODES.get(node_id)


def are_connected(from_id: str, to_id: str) -> bool:
    src = get_node(from_id)
    if not src:
        return False
    return to_id in src["connections"] or to_id in sorted(set(src["connections"]))


def travel_cost(from_id: str, to_id: str) -> Tuple[float, float]:
    """Returns (qi_cost_fraction_of_max, cooldown_minutes)."""
    dst = get_node(to_id)
    danger = dst["danger_tier"] if dst else 1
    cooldown = (
        WORLD["travel_cooldown_base_minutes"]
        + danger * WORLD["travel_cooldown_per_danger"]
    )
    return WORLD["travel_qi_cost_pct"], round(cooldown, 1)


# ── Encounters ───────────────────────────────────────────────────────

def _encounter_weights(danger_tier: int) -> List[Tuple[str, float]]:
    weighted = []
    for enc_type, cfg in ENCOUNTERS.items():
        w = max(0.5, cfg["base_weight"] + cfg["danger_scaling"] * danger_tier)
        weighted.append((enc_type, w))
    return weighted


def roll_encounter(node: Dict[str, Any], rng: Optional[random.Random] = None) -> str:
    """Danger reshapes the wilds: deeper nodes hide more caves and teeth."""
    rng = rng or random
    pairs = _encounter_weights(node["danger_tier"])
    types = [t for t, _ in pairs]
    weights = [w for _, w in pairs]
    return rng.choices(types, weights=weights, k=1)[0]


def find_herb(realm: int, danger_tier: int, luck_stat: int, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """Herb age scales with BOTH realm and local danger (rich lands grow old growth)."""
    rng = rng or random
    from core.balance import HERB_ELEMENTS
    element = rng.choice(HERB_ELEMENTS)
    effective_realm = realm + int(danger_tier * ENCOUNTER_TUNING["herb_age_danger_bonus"])
    tiers = _age_tier_weights(effective_realm)
    age = rng.choices([100, 500, 1000, 10000], weights=tiers, k=1)[0]
    item = HERBS[f"herb_{element.lower()}_{age}"]
    qty = 1 if age >= 10000 else rng.randint(1, 2)
    return {"item": item, "qty": qty}


def find_mineral(danger_tier: int, realm: int, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """Vein depth follows the land's danger, not the miner."""
    rng = rng or random
    max_tier = min(5, 1 + danger_tier // 2)
    pool = [m for m in MINERALS.values() if m["tier"] <= max(1, max_tier)]
    weights = [m["gather_weight"] for m in pool]
    item = rng.choices(pool, weights=weights, k=1)[0]
    qty = rng.randint(1, 3) if item["tier"] <= 2 else 1
    return {"item": item, "qty": qty}


# ── Ancient Cave Abode gamble ────────────────────────────────────────

def resolve_cave_gamble(danger_tier: int, luck_stat: int, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """
    A Dongfu left behind by some dead master. High risk, legacy reward.
    Success: insight + stones (+ a rare old-growth herb at higher danger).
    Trap: meridian scarring and lighter purse.
    """
    rng = rng or random
    chance = ENCOUNTER_TUNING["cave_success_chance_base"] + luck_stat * 0.005 - danger_tier * 0.01
    chance = max(0.15, min(0.9, chance))

    if rng.random() <= chance:
        lo, hi = ENCOUNTER_TUNING["cave_reward_insight_range"]
        insight = rng.randint(lo, hi) + danger_tier // 2
        slo, shi = ENCOUNTER_TUNING["cave_reward_stones_range"]
        stones = int(rng.randint(slo, shi) * (1 + danger_tier * 0.25))
        reward_item = None
        if danger_tier >= 4:
            candidates = [h for h in HERBS.values() if h["age_years"] >= ENCOUNTER_TUNING["cave_reward_herb_age_min"]]
            reward_item = rng.choice(candidates)
        return {
            "success": True,
            "insight": insight,
            "stones": stones,
            "reward_item": reward_item,
            "message": (
                f"🏛️ The cave abode's ward recognizes your bearing! Within: a jade slip of lost "
                f"insight (+{insight} Dao Insight) and a spirit-stone cache ({stones} low-grade)."
                + (f" A {reward_item['name']} rests on a stone dais!" if reward_item else "")
            ),
        }

    tlo, thi = ENCOUNTER_TUNING["cave_trap_meridian_damage"]
    trap_meridian = round(rng.uniform(tlo, thi), 3)
    qi_loss = ENCOUNTER_TUNING["cave_trap_qi_loss_ratio"]
    return {
        "success": False,
        "meridian_damage": trap_meridian,
        "qi_loss_ratio": qi_loss,
        "message": (
            f"☠️ TRAP! The abode was a demon's larder, not a sage's home. Formations flare — "
            f"you barely crawl out (Meridian Damage +{trap_meridian:.0%})."
        ),
    }


# ── Ambush clash ─────────────────────────────────────────────────────

def compute_player_power(
    realm: int,
    stage_index: int,
    equipped_artifact_powers: float,
    physique_tier: int,
    luck_stat: int
) -> float:
    t = ENCOUNTER_TUNING
    return round(
        realm * t["player_realm_weight"]
        + stage_index * t["player_stage_weight"]
        + equipped_artifact_powers / t["player_artifact_divisor"]
        + physique_tier * t["player_physique_weight"]
        + luck_stat * t["player_luck_weight"],
        2,
    )


def resolve_ambush(
    player_power: float,
    danger_tier: int,
    wallet_stones: int,
    choice: str,
    rng: Optional[random.Random] = None
) -> Dict[str, Any]:
    """
    Lightweight clash until a full combat engine exists.
    choice: "fight" | "flee". Never lethal (tribulations hold that monopoly).
    """
    rng = rng or random
    vlo, vhi = ENCOUNTER_TUNING["enemy_variance"]
    enemy_power = danger_tier * ENCOUNTER_TUNING["enemy_power_per_danger"] * rng.uniform(vlo, vhi)

    if choice == "flee":
        chance = (
            ENCOUNTER_TUNING["flee_base_chance"]
            + ENCOUNTER_TUNING["flee_per_luck"] * 5  # neutral baseline luck assumption baked into base
            - danger_tier * ENCOUNTER_TUNING["flee_per_danger_penalty"]
        )
        chance = max(0.10, min(0.90, chance))
        if rng.random() <= chance:
            return {"result": "ESCAPED", "message": "💨 You blur into the terrain and lose your pursuers among the rocks."}
        choice = "fight"  # caught fleeing → forced clash at a disadvantage
        enemy_power *= 1.15

    win_chance = max(0.05, min(0.95, player_power / max(1.0, player_power + enemy_power)))
    if rng.random() <= win_chance:
        slo, shi = ENCOUNTER_TUNING["win_loot_stones_range"]
        loot = int(rng.randint(slo, shi) * (1 + danger_tier * 0.3))
        return {
            "result": "VICTORY",
            "loot_stones": loot,
            "message": (
                f"⚔️ CLASH! Your power crushes the ambusher's killing intent. You loot "
                f"{loot} spirit stones from its corpse/nascent-pouch."
            ),
        }

    mlo, mhi = ENCOUNTER_TUNING["loss_meridian_damage_range"]
    meridian = round(rng.uniform(mlo, mhi), 3)
    lost_stones = int(wallet_stones * ENCOUNTER_TUNING["loss_stone_loss_ratio"])
    return {
        "result": "DEFEAT",
        "meridian_damage": meridian,
        "lost_stones": lost_stones,
        "message": (
            f"🩸 The beast/rogue cultivator overwhelms you! You escape with ruptured meridians "
            f"(+{meridian:.0%} damage) and a lighter pouch (-{lost_stones} stones)."
        ),
    }
