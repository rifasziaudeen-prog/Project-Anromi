import random
from typing import Dict, Any, Tuple

from core.balance import ROOTS, PHYSIQUES, get_root_config, get_physique_config


def roll_root(luck_bonus: float = 0.0, rng: random.Random | None = None) -> Tuple[str, float]:
    """
    Weighted celestial gacha roll for a spiritual root.
    luck_bonus (0.0 - 1.0) shifts probability weight from the two common
    roots onto rare+ roots (used for reincarnation karmic blessings).
    Returns: (root_name, rolled_purity)
    """
    rng = rng or random
    luck_bonus = max(0.0, min(1.0, luck_bonus))

    names = list(ROOTS.keys())
    weights = [ROOTS[name]["roll_weight"] for name in names]

    if luck_bonus > 0:
        # Karmic luck drains the mortal-tier pool and pours it into Epic+ talent
        low_tiers = {"Common", "Uncommon", "Rare"}
        high_tiers = {"Epic", "Legendary", "Mythic", "Celestial"}
        low_total = sum(
            w for n, w in zip(names, weights) if ROOTS[n]["rarity"] in low_tiers
        )
        high_total = sum(
            w for n, w in zip(names, weights) if ROOTS[n]["rarity"] in high_tiers
        )
        if high_total > 0 and low_total > 0:
            drain = low_total * luck_bonus
            scale = (high_total + drain) / high_total
            weights = [
                w * scale if ROOTS[n]["rarity"] in high_tiers
                else w * (1.0 - luck_bonus)
                for n, w in zip(names, weights)
            ]

    chosen = rng.choices(names, weights=weights, k=1)[0]
    cfg = ROOTS[chosen]
    lo, hi = cfg["purity_range"]
    purity = round(rng.uniform(lo, hi), 2)
    return chosen, purity


def roll_physique(rng: random.Random | None = None) -> Tuple[str, int]:
    """Weighted roll for a body constitution. Returns: (physique_name, tier)."""
    rng = rng or random
    names = list(PHYSIQUES.keys())
    weights = [PHYSIQUES[name]["roll_weight"] for name in names]
    chosen = rng.choices(names, weights=weights, k=1)[0]
    return chosen, PHYSIQUES[chosen]["tier"]


def get_absorption_multiplier(root_name: str, root_purity: float = 0.5) -> float:
    """
    Final absorption multiplier = root base × purity scaling.
    Purity adds up to +50% on top of the root's base multiplier.
    """
    cfg = get_root_config(root_name)
    return cfg["absorption_multiplier"] * (1.0 + max(0.0, min(1.0, root_purity)) * 0.5)


def get_root_summary(root_name: str) -> Dict[str, Any]:
    """Full public info card for a root (for UI display)."""
    cfg = get_root_config(root_name)
    return {
        "name": root_name,
        "rarity": cfg["rarity"],
        "elements": cfg["elements"],
        "blurb": cfg["blurb"],
    }


def get_physique_summary(physique_name: str) -> Dict[str, Any]:
    cfg = get_physique_config(physique_name)
    return {
        "name": physique_name,
        "tier": cfg["tier"],
        "qi_absorption_bonus": cfg["qi_absorption_bonus"],
        "tribulation_resistance": cfg["tribulation_resistance"],
        "dao_heart_guard": cfg["dao_heart_guard"],
        "blurb": cfg["blurb"],
    }
