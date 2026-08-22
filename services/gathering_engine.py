"""
Gathering Engine — placeholder forager until the v0.4 world engine.
Cooldown-gated herb picking / ore prospecting with realm- and luck-scaled rarity.
All tunables in balance → GATHERING.
"""
import random
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from core.balance import GATHERING, HERBS, MINERALS, LUCK, HERB_ELEMENTS


def gather_cooldown_remaining(last_gathered: Optional[datetime], now: Optional[datetime] = None) -> float:
    """Minutes until the next gather is allowed. 0.0 = ready."""
    if last_gathered is None:
        return 0.0
    now = now or datetime.now(timezone.utc)
    if last_gathered.tzinfo is None:
        last_gathered = last_gathered.replace(tzinfo=timezone.utc)
    elapsed_min = (now - last_gathered).total_seconds() / 60.0
    return max(0.0, round(GATHERING["cooldown_minutes"] - elapsed_min, 2))


def _age_tier_weights(realm: int) -> List[float]:
    """Older growth becomes likelier as realm rises (multiplicative scaling)."""
    base = list(GATHERING["age_tier_weights_base"])
    scalings = GATHERING["age_tier_realm_scaling"]
    exponent = max(1, realm) - 1
    return [w * (s ** exponent) for w, s in zip(base, scalings)]


def roll_herb(realm: int, luck_stat: int, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    rng = rng or random
    element = rng.choice(list(HERB_ELEMENTS))
    tier_weights = _age_tier_weights(max(1, realm))
    ages = [100, 500, 1000, 10000]
    age = rng.choices(ages, weights=tier_weights, k=1)[0]
    return HERBS[f"herb_{element.lower()}_{age}"]


def roll_mineral(realm: int, luck_stat: int, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    rng = rng or random
    realm_gate = min(5, max(1, realm))
    pool = [m for m in MINERALS.values() if m["tier"] <= realm_gate]
    weights = []
    for m in pool:
        w = m["gather_weight"]
        if m["tier"] >= 3:
            w *= 1 + luck_stat * LUCK["gather_rare_shift_per_point"] * 0.2
        weights.append(w)
    return rng.choices(pool, weights=weights, k=1)[0]


def execute_gather(realm: int, luck_stat: int, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """
    One foraging expedition outcome. Nothing here touches the DB.
    """
    rng = rng or random
    roll = rng.random()
    if roll < GATHERING["herb_chance"]:
        item = roll_herb(realm, luck_stat, rng)
        qty = rng.randint(1, 2) if item["age_years"] < 10000 else 1
        flavor = "You pry a spirit herb from between mossy stones."
        return {"found": True, "kind": "Herb", "item": item, "qty": qty,
                "message": f"🌿 {flavor} Acquired {item['name']} x{qty}."}
    elif roll < GATHERING["herb_chance"] + GATHERING["mineral_chance"]:
        item = roll_mineral(realm, luck_stat, rng)
        qty = rng.randint(1, 3) if item["tier"] <= 2 else 1
        return {"found": True, "kind": "Mineral", "item": item, "qty": qty,
                "message": f"⛏️ Your pickaxe rings against something dense! Acquired {item['name']} x{qty}."}
    else:
        return {"found": False, "kind": None, "item": None, "qty": 0,
                "message": "🍂 You wander for hours but find only mortal weeds. The land yields nothing today."}
