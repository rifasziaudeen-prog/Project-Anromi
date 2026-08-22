"""
Forging Engine (Qi Dao) — artifact crafting.
Success is skill-gated by mastery level and artifact tier; failure still
teaches (XP) but devours half the materials. All tunables in balance → FORGING.
"""
import random
from typing import Dict, Any, Optional

from core.balance import FORGING


def calculate_success_chance(artifact: Dict[str, Any], forging_level: int) -> float:
    base = FORGING["success_base_by_tier"].get(artifact["tier"], 0.5)
    chance = base + max(0, forging_level - 1) * FORGING["success_per_level"]
    return round(min(FORGING["success_cap"], max(0.05, chance)), 4)


def attempt_forge(
    artifact: Dict[str, Any],
    forging_level: int,
    rng: Optional[random.Random] = None
) -> Dict[str, Any]:
    """
    Resolves one forge attempt. Materials are consumed by the caller;
    this returns the outcome + how much of each material survives failure.
    """
    rng = rng or random
    chance = calculate_success_chance(artifact, forging_level)
    roll = rng.random()
    success = roll <= chance

    result: Dict[str, Any] = {
        "success": success,
        "roll": round(roll, 4),
        "chance": chance,
        "xp_gain": FORGING["xp_by_tier"].get(artifact["tier"], 20),
        "lost_materials": {},
    }

    if success:
        result["message"] = (
            f"🔨 HAMMER FALLS! The {artifact['name']} screams out of the quench-bath, "
            f"spirit-light rippling across its surface. It is DONE!"
        )
        return result

    # Failure: half of every material cracks apart
    for mat_id, qty in artifact["materials"].items():
        lost = max(1, int(round(qty * FORGING["fail_material_loss_ratio"])))
        result["lost_materials"][mat_id] = lost
    result["xp_gain"] = int(round(result["xp_gain"] * FORGING["fail_xp_ratio"]))
    result["message"] = (
        f"💥 The quenching FAILS — hairline fractures spider across the {artifact['name']}! "
        f"The artifact shatters; part of your materials are slag now. But your hands remember."
    )
    return result


def xp_to_level(exp: int) -> Dict[str, Any]:
    return _level_from_exp(exp, FORGING["xp_curve"], FORGING["level_titles"])


def mastery_title(level: int) -> str:
    return FORGING["level_titles"][min(len(FORGING["level_titles"]), max(1, level)) - 1]


def _level_from_exp(exp: int, curve: list, titles: list) -> Dict[str, Any]:
    level = 1
    for i, threshold in enumerate(curve):
        if exp >= threshold:
            level = i + 1
    level = min(level, len(curve))
    current_floor = curve[level - 1]
    next_req = curve[level] if level < len(curve) else None
    return {
        "level": level,
        "exp": exp,
        "next_level_exp": next_req,
        "exp_into_level": exp - current_floor,
        "title": titles[min(len(titles), max(1, level)) - 1],
    }
