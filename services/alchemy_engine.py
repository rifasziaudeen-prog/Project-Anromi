"""
Alchemy Engine (Dan Dao) — pill brewing driven by IMPURITY, not luck alone.

Quality philosophy:
- Every brew produces an impurity value [0,100]. Lower = purer = better grade.
- MASTERY lowers the impurity floor AND narrows randomness (consistency).
- LUCK only fires occasional "heavenly coincidences" that drop impurity
  dramatically. Pure luck can NEVER produce consistent top grades.
- Toxicity on consumption derives from residual impurities — a Flawless
  pill (0 impurities) has ZERO side effects.
All tunables live in core/balance.py → ALCHEMY.
"""
import random
from typing import Dict, Any, Optional

from core.balance import ALCHEMY


def grade_from_impurity(impurity: float) -> str:
    if impurity < ALCHEMY["flawless_hard_max"]:
        return "Flawless"
    if impurity <= ALCHEMY["grade_thresholds"]["top_max"]:
        return "Top"
    if impurity <= ALCHEMY["grade_thresholds"]["medium_max"]:
        return "Medium"
    return "Low"


def _coincidence_chance(luck_stat: int) -> float:
    return min(
        0.5,
        ALCHEMY["coincidence_base_chance"] + max(0, luck_stat) * ALCHEMY["coincidence_per_luck"]
    )


def compute_impurity(
    recipe: Dict[str, Any],
    furnace_impurity_reduction: float,
    flame_impurity_reduction: float,
    alchemy_level: int,
    luck_stat: int,
    rng: Optional[random.Random] = None
) -> Dict[str, Any]:
    """
    The purity contest between craftsman and heaven.
    Returns the rolled impurity, its breakdown, and whether a heavenly
    coincidence fired.
    """
    rng = rng or random
    level = max(1, alchemy_level)

    center = (
        recipe["base_impurity"]
        - furnace_impurity_reduction
        - flame_impurity_reduction
        - (level * ALCHEMY["mastery_control_per_level"])
    )
    spread = max(
        ALCHEMY["spread_min"],
        ALCHEMY["spread_base"] - (level * ALCHEMY["spread_shrink_per_level"])
    )

    impurity = rng.gauss(max(0.0, center), spread)
    impurity = max(0.0, min(100.0, impurity))

    # Heavenly Coincidence — luck's ONLY lever, and it cannot save the unskilled:
    # it multiplies residual impurity, so only near-pure brews can reach Flawless.
    coincidence_fired = False
    if rng.random() < _coincidence_chance(luck_stat):
        coincidence_fired = True
        impurity *= ALCHEMY["coincidence_impurity_factor"]

    return {
        "impurity": round(impurity, 2),
        "center": round(center, 2),
        "spread": round(spread, 2),
        "heavenly_coincidence": coincidence_fired,
        "grade": grade_from_impurity(impurity),
    }


def grade_potency(grade: str) -> float:
    return ALCHEMY["grade_potency"].get(grade, 1.0)


def apply_recipe_effects(recipe: Dict[str, Any], grade: str) -> Dict[str, Any]:
    """Scales every recipe effect by the quality-grade potency multiplier."""
    mult = grade_potency(grade)
    return {
        key: round(value * mult, 4) for key, value in recipe.get("effects", {}).items()
    }


def consumption_toxicity(grade: str) -> float:
    """Residual impurities poison the drinker — except at Flawless."""
    nominal = ALCHEMY["grade_nominal_impurity"].get(grade, 45.0)
    return round(nominal * ALCHEMY["toxicity_per_impurity_point"], 2)


def xp_gain(recipe: Dict[str, Any], grade: str) -> int:
    return int(round(recipe["xp_reward"] * ALCHEMY["grade_xp_bonus"].get(grade, 1.0)))


def level_from_exp(exp: int, curve: Optional[list] = None) -> Dict[str, Any]:
    """curve[i] = total XP required to be AT level i+1. Returns level + progress."""
    curve = curve or ALCHEMY["xp_curve"]
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
        "title": mastery_title(level),
    }


def mastery_title(level: int) -> str:
    titles = ALCHEMY["level_titles"]
    return titles[min(len(titles), max(1, level)) - 1]


def refine_outcome_message(grade: str, coincidence: bool, pill_name: str) -> str:
    if grade == "Flawless":
        base = (
            f"🌟 FLAWLESS HEAVEN-GRADE PILL! The {pill_name} emerges utterly pure — "
            f"not a single impurity dares remain! Pill light pierces the clouds!"
        )
    elif grade == "Top":
        base = f"✨ The furnace opens: a TOP-grade {pill_name}, fragrant and nearly pure!"
    elif grade == "Medium":
        base = f"☁️ A serviceable {pill_name} — medium grade, faint impurities swirling within."
    else:
        base = f"🥴 The {pill_name} came out murky and speckled... low grade. It will work, but your meridians will pay."
    if coincidence and grade != "Flawless":
        base += " (A heavenly coincidence steadied your flame mid-brew!)"
    return base
