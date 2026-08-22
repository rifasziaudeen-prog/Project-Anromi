import random
import math
from datetime import datetime, timezone
from typing import Tuple, Dict, Any, Optional

from models.realm import (
    RealmTier,
    REALM_METADATA,
    get_realm_meta,
    get_stages_for_realm,
    is_bottleneck_stage
)
from core.balance import BREAKTHROUGH, BACKLASH, DAO_HEART, SOUL, ALCHEMY
from services.root_engine import get_absorption_multiplier


def calculate_passive_energy_recovery(
    current_energy: float,
    max_energy: float,
    last_meditated: datetime,
    realm: int,
    stage: str,
    root: str = "Mortal Five-Element",
    root_purity: float = 0.5,
    meridian_damage: float = 0.0,
    ambient_spirit_density: float = 1.0,
    physique_absorption_bonus: float = 0.0,
    equipment_qi_bonus: float = 0.0,
    pill_toxicity: float = 0.0
) -> Tuple[float, float]:
    """
    Calculates passive Qi absorption over simulated elapsed time with diminishing returns,
    meridian health, environmental spirit density, physique/equipment bonuses,
    and Pill Toxicity (*Dan Du*) stalling factoring.
    Returns: (new_current_energy, energy_gathered)
    """
    now = datetime.now(timezone.utc)
    if last_meditated.tzinfo is None:
        last_meditated = last_meditated.replace(tzinfo=timezone.utc)

    minutes_passed = (now - last_meditated).total_seconds() / 60.0
    if minutes_passed <= 0:
        return current_energy, 0.0

    meta = get_realm_meta(realm)
    base_rate = meta.get("base_absorption_rate", 1.0)
    root_mult = get_absorption_multiplier(root, root_purity)
    meridian_efficiency = max(0.10, 1.0 - meridian_damage)

    # Pill Toxicity clogs the meridians with medicinal dregs
    toxicity_stall = max(0.0, min(100.0, pill_toxicity)) / 100.0 * ALCHEMY["absorption_stall_scale"]
    meridian_efficiency *= (1.0 - toxicity_stall)

    # Diminishing returns as meridian nears full capacity
    fullness_ratio = min(1.0, current_energy / max(1.0, max_energy))
    diminishing_factor = max(0.15, math.pow(max(0.01, 1.0 - fullness_ratio), 0.35))

    rate_per_minute = (
        base_rate
        * root_mult
        * (1.0 + max(0.0, physique_absorption_bonus))
        * (1.0 + max(0.0, equipment_qi_bonus))
        * ambient_spirit_density
        * meridian_efficiency
        * diminishing_factor
    )
    gathered = rate_per_minute * minutes_passed

    new_energy = min(max_energy, current_energy + gathered)
    actual_gathered = new_energy - current_energy
    return new_energy, actual_gathered


def check_cultivation_deviation(
    dao_heart: float,
    rng: Optional[random.Random] = None
) -> Optional[Dict[str, Any]]:
    """
    Zou Huo Ru Mo — Qi Deviation risk when Dao Heart falls below threshold.
    Chance scales with how deep below the threshold stability has fallen.
    Returns an episode dict, or None if stable / no episode triggered.
    """
    threshold = DAO_HEART["deviation_threshold"]
    if dao_heart >= threshold:
        return None

    depth_ratio = (threshold - dao_heart) / max(1.0, threshold)
    chance = min(0.75, DAO_HEART["deviation_base_chance"] * (0.5 + depth_ratio))
    rng = rng or random
    if rng.random() > chance:
        return None

    return {
        "triggered": True,
        "qi_loss_ratio": DAO_HEART["deviation_qi_loss_ratio"],
        "dao_heart_loss": DAO_HEART["deviation_dao_heart_loss"],
        "karma_gain": DAO_HEART["deviation_karma_gain"],
        "message": (
            "🩸 QI DEVIATION! Turbulent energy runs WILD through your meridians like a cornered "
            "dragon! You cough blood as inner demons whisper from the void. Your Dao Heart wavers!"
        ),
    }


def calculate_breakthrough_odds(
    realm: int,
    stage: str,
    current_energy: float,
    max_energy: float,
    qi_purity: float = 0.75,
    dao_heart: float = 100.0,
    meridian_damage: float = 0.0,
    bottleneck_insight: float = 0.0,
    pill_bonus: float = 0.0,
    pill_toxicity: float = 0.0
) -> Dict[str, Any]:
    """
    Calculates detailed transparent breakthrough odds and modifiers.
    All scales tunable in core/balance.py → BREAKTHROUGH.
    Pill Toxicity (*Dan Du*) poisons the attempt; booster pills offset it.
    """
    meta = get_realm_meta(realm)
    stages = meta["stages"]
    is_bottleneck = is_bottleneck_stage(realm, stage)
    is_realm_leap = (stage == stages[-1]) # Attempting to leap to next realm

    # Minimum Qi requirement to attempt
    min_required_energy = max_energy * BREAKTHROUGH["min_qi_ratio"]
    can_attempt = current_energy >= min_required_energy

    if not can_attempt:
        return {
            "can_attempt": False,
            "required_energy": min_required_energy,
            "current_energy": current_energy,
            "final_chance": 0.0,
            "reason": f"Insufficient Qi! Meridian requires at least {min_required_energy:.1f} Qi ({BREAKTHROUGH['min_qi_ratio']:.0%}) to attempt breakthrough."
        }

    # Baseline probability calculation
    if is_realm_leap:
        base_chance = 0.05
        for cap, chance in BREAKTHROUGH["realm_leap_base"]:
            if realm <= cap:
                base_chance = chance
                break
    elif is_bottleneck:
        base_chance = BREAKTHROUGH["bottleneck_chance_mortal"] if realm <= 8 else BREAKTHROUGH["bottleneck_chance_immortal"]
    else:
        base_chance = BREAKTHROUGH["standard_chance_mortal"] if realm <= 8 else BREAKTHROUGH["standard_chance_immortal"]

    # Modifiers
    fullness_bonus = ((current_energy / max_energy) - BREAKTHROUGH["min_qi_ratio"]) * BREAKTHROUGH["fullness_bonus_scale"]
    purity_bonus = (qi_purity - BREAKTHROUGH["purity_midpoint"]) * BREAKTHROUGH["purity_bonus_scale"]
    safe_zone = BREAKTHROUGH["dao_heart_safe_zone"]
    dao_heart_mod = 0.0 if dao_heart >= safe_zone else ((dao_heart - safe_zone) / 100.0) * BREAKTHROUGH["dao_heart_penalty_scale"]
    meridian_penalty = -(meridian_damage * BREAKTHROUGH["meridian_penalty_scale"])
    insight_bonus = min(BREAKTHROUGH["insight_bonus_cap"], bottleneck_insight * BREAKTHROUGH["insight_per_point"])
    toxicity_penalty = -(max(0.0, min(100.0, pill_toxicity)) / 100.0 * ALCHEMY["breakthrough_penalty_scale"])

    raw_chance = base_chance + fullness_bonus + purity_bonus + dao_heart_mod + meridian_penalty + insight_bonus + toxicity_penalty + pill_bonus
    final_chance = max(BREAKTHROUGH["chance_floor"], min(BREAKTHROUGH["chance_ceiling"], raw_chance))

    return {
        "can_attempt": True,
        "is_bottleneck": is_bottleneck,
        "is_realm_leap": is_realm_leap,
        "base_chance": round(base_chance, 4),
        "modifiers": {
            "fullness_bonus": round(fullness_bonus, 4),
            "purity_bonus": round(purity_bonus, 4),
            "dao_heart_mod": round(dao_heart_mod, 4),
            "meridian_penalty": round(meridian_penalty, 4),
            "insight_bonus": round(insight_bonus, 4),
            "pill_bonus": round(pill_bonus, 4)
        },
        "final_chance": round(final_chance, 4),
        "target_realm": realm + 1 if is_realm_leap else realm,
        "target_stage": "Layer 1" if (is_realm_leap and (realm + 1) < 9) else ("Early Stage" if is_realm_leap else stages[stages.index(stage) + 1])
    }


def _roll_backlash(rng: random.Random) -> Dict[str, Any]:
    """Weighted pick from the BACKLASH severity table."""
    severities = [b["severity"] for b in BACKLASH]
    weights = [b["weight"] for b in BACKLASH]
    chosen = rng.choices(severities, weights=weights, k=1)[0]
    return next(b for b in BACKLASH if b["severity"] == chosen)


def execute_breakthrough(
    realm: int,
    stage: str,
    current_energy: float,
    max_energy: float,
    qi_purity: float = 0.75,
    dao_heart: float = 100.0,
    meridian_damage: float = 0.0,
    bottleneck_insight: float = 0.0,
    pill_bonus: float = 0.0,
    physique_guard: float = 0.0,
    pill_toxicity: float = 0.0
) -> Dict[str, Any]:
    """
    Executes a breakthrough attempt, resolving layer advancement, realm leaps,
    or backlash penalties. Physique dao_heart_guard softens emotional trauma.
    May flag body_destroyed=True on total meridian rupture (permadeath hook).
    """
    odds = calculate_breakthrough_odds(
        realm, stage, current_energy, max_energy,
        qi_purity, dao_heart, meridian_damage, bottleneck_insight,
        pill_bonus, pill_toxicity
    )

    if not odds["can_attempt"]:
        return {
            "success": False,
            "outcome": "INSUFFICIENT_QI",
            "message": odds["reason"],
            "realm": realm,
            "stage": stage,
            "current_energy": current_energy,
            "max_energy": max_energy,
            "dao_heart": dao_heart,
            "meridian_damage": meridian_damage,
            "is_dead": False,
            "is_remnant_soul": False,
            "near_miss": False,
            "consolation_insight": 0,
            "body_destroyed": False
        }

    rng = random.Random()
    roll = rng.random()
    success = roll <= odds["final_chance"]
    stages = get_stages_for_realm(realm)
    curr_idx = stages.index(stage) if stage in stages else 0

    if success:
        # Check if advancing stage or realm leap
        if curr_idx < len(stages) - 1:
            # Advance to next layer / sub-stage
            new_realm = realm
            new_stage = stages[curr_idx + 1]
            meta = get_realm_meta(new_realm)
            mult = meta.get("qi_multiplier_per_stage", 1.25)
            new_max_energy = max_energy * mult
            new_current_energy = max_energy * BREAKTHROUGH["layer_advance_energy_pct"]
            msg = f"✨ Breakthrough Successful! You have broken through to {meta['name_en']} ({new_stage})!"
        else:
            # Leap to next realm!
            new_realm = realm + 1
            new_meta = get_realm_meta(new_realm)
            new_stage = new_meta["stages"][0]
            new_max_energy = new_meta["base_max_qi"]
            new_current_energy = new_max_energy * BREAKTHROUGH["realm_leap_energy_pct"]
            msg = f"⚡ HEAVEN DEFYING! You have shattered the mortal shackles and stepped into the {new_meta['name_en']} Realm ({new_stage})!"

        # Success cleanses slight meridian damage & boosts Dao Heart
        new_meridian_damage = max(0.0, meridian_damage - BREAKTHROUGH["success_meridian_heal"])
        new_dao_heart = min(100.0, dao_heart + BREAKTHROUGH["success_dao_heart_gain"])

        return {
            "success": True,
            "outcome": "SUCCESS",
            "message": msg,
            "roll": round(roll, 4),
            "needed": odds["final_chance"],
            "realm": new_realm,
            "stage": new_stage,
            "current_energy": round(new_current_energy, 2),
            "max_energy": round(new_max_energy, 2),
            "dao_heart": round(new_dao_heart, 2),
            "meridian_damage": round(new_meridian_damage, 2),
            "is_dead": False,
            "is_remnant_soul": False,
            "near_miss": False,
            "consolation_insight": 0,
            "body_destroyed": False
        }
    else:
        # Failure Backlash Resolution (weighted severity table)
        backlash = _roll_backlash(rng)

        lost_energy = current_energy * backlash["qi_loss_ratio"]
        new_energy = max(0.0, current_energy - lost_energy)
        new_meridian_dmg = min(1.0, meridian_damage + backlash["meridian_damage"])
        raw_dh_loss = backlash["dao_heart_loss"] - max(0.0, physique_guard)
        new_dao_heart = max(0.0, dao_heart - max(0.0, raw_dh_loss))

        regressed_realm = realm
        regressed_stage = stage

        if backlash["severity"] == "MINOR":
            msg = f"❌ Breakthrough Failed. Your Qi dissipated and turbulent energy caused minor meridian friction. (Lost {lost_energy:.1f} Qi)"
        elif backlash["severity"] == "MODERATE":
            msg = f"💥 Breakthrough Backlash! Spiritual energy rebounded violently, rupturing your meridians! (Meridian Damage +{backlash['meridian_damage']:.0%}, Dao Heart -{raw_dh_loss:g})"
        else: # CATASTROPHIC
            if backlash["stage_regression"] and curr_idx > 0:
                regressed_stage = stages[curr_idx - 1]
                msg = f"⚠️ CATASTROPHIC BACKLASH! The Will of the Heavens crushed your foundation! You have regressed to {stages[curr_idx - 1]}!"
            else:
                msg = "⚠️ CATASTROPHIC BACKLASH! Your foundation cracked and Qi deviated wildly! Severe trauma sustained!"

        # Near-miss psychology: agonizingly close failures fuel the retry loop
        near_miss = not success and (odds["final_chance"] - roll) > 0
        consolation_insight = 0
        if near_miss:
            from services.engagement_engine import check_near_miss, near_miss_message
            if check_near_miss(roll, odds["final_chance"]):
                from core.balance import ENGAGEMENT
                consolation_insight = ENGAGEMENT["near_miss_consolation_insight"]
                msg += " " + near_miss_message()
                if consolation_insight > 0:
                    msg += f" (+{consolation_insight} Dao Insight earned from the near-miss!)"

        # Permadeath hook: total meridian rupture destroys the body
        body_destroyed = (
            SOUL["body_destroyed_on_total_rupture"]
            and backlash["severity"] == "CATASTROPHIC"
            and new_meridian_dmg >= 1.0
        )
        if body_destroyed:
            msg += " 🌋 Your meridians BURST apart — your body begins to come undone at the seams..."

        return {
            "success": False,
            "outcome": "FAILURE",
            "message": msg,
            "roll": round(roll, 4),
            "needed": odds["final_chance"],
            "severity": backlash["severity"],
            "realm": regressed_realm,
            "stage": regressed_stage,
            "current_energy": round(new_energy, 2),
            "max_energy": max_energy,
            "dao_heart": round(new_dao_heart, 2),
            "meridian_damage": round(new_meridian_dmg, 2),
            "is_dead": body_destroyed,
            "is_remnant_soul": False,
            "near_miss": near_miss,
            "consolation_insight": consolation_insight,
            "body_destroyed": body_destroyed
        }
