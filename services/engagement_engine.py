"""
Engagement Psychology Engine — habit loops, variable rewards, loss framing.
All tunables live in core/balance.py → ENGAGEMENT.
"""
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, Optional

from core.balance import ENGAGEMENT, LUCK


# ── Streaks ─────────────────────────────────────────────────────────

def today_str(now: Optional[datetime] = None) -> str:
    return (now or datetime.now(timezone.utc)).strftime("%Y-%m-%d")


def update_streak(last_action_date: Optional[str], current_streak: int, now: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Calendar-day streak resolution (UTC).
    Same day → streak holds. Yesterday → streak grows. Older → reset to 1.
    """
    now = now or datetime.now(timezone.utc)
    today = today_str(now)
    yesterday = today_str(now - timedelta(days=1))

    if last_action_date == today:
        new_streak = max(1, current_streak)
        changed = False
        msg = f"Day {new_streak} of your meditation saga continues."
    elif last_action_date == yesterday:
        new_streak = current_streak + 1
        changed = True
        msg = f"🔥 Streak extended! {new_streak} consecutive days of unwavering Dao."
    else:
        new_streak = 1
        changed = True
        msg = "Your chain of discipline was broken... a new saga begins at Day 1."

    return {
        "streak_days": new_streak,
        "changed": changed,
        "multiplier": get_streak_multiplier(new_streak),
        "message": msg,
    }


def get_streak_multiplier(streak_days: int) -> float:
    """Highest threshold reached wins. e.g. day 7 → 1.25x Qi gain."""
    multiplier = 1.0
    for threshold, mult in sorted(ENGAGEMENT["streak_multipliers"], key=lambda x: x[0]):
        if streak_days >= threshold:
            multiplier = mult
    return multiplier


# ── Near-Miss Effect ────────────────────────────────────────────────

def check_near_miss(roll: float, needed: float) -> bool:
    """
    True when a failed breakthrough came agonizingly close.
    Near-misses fire the same brain circuits as wins — players retry.
    """
    if needed <= 0:
        return False
    return 0.0 < (needed - roll) <= ENGAGEMENT["near_miss_threshold"]


NEAR_MISS_LINES = [
    "SO CLOSE! The heavens trembled as your Qi surged — mere inches from shattering through!",
    "AGONY! The barrier CRACKED under your will... but held. You were inches from glory!",
    "Your aura exploded outward — the bottleneck SHUDDERED. One more push and it breaks!",
]


def near_miss_message() -> str:
    return random.choice(NEAR_MISS_LINES)


# ── Variable-Ratio Windfalls ────────────────────────────────────────

def maybe_windfall(rng: Optional[random.Random] = None, luck_stat: int = 5) -> Optional[Dict[str, Any]]:
    """
    Random jackpot during meditation: Dao Insight (+bottleneck comprehension)
    and sometimes spirit stones. Unpredictable rewards are maximally addictive.
    The Luck stat bends the odds.
    """
    rng = rng or random
    chance = ENGAGEMENT["windfall_chance"] * (1.0 + max(0, luck_stat) * LUCK["windfall_chance_per_point"])
    if rng.random() >= chance:
        return None

    lo, hi = ENGAGEMENT["windfall_insight_range"]
    reward: Dict[str, Any] = {
        "type": "DAO_INSIGHT",
        "insight": rng.randint(lo, hi),
        "spirit_stones": 0,
        "message": "",
    }

    lines = [
        "🌟 EPIPHANY! A fragment of heavenly Dao flowed into your mind mid-breath!",
        "💫 Your heart suddenly stilled — profound insight crystallizes in your Dantian!",
        "🌀 The ambient Qi swirled into a vortex around you, whispering lost secrets!",
    ]
    reward["message"] = rng.choice(lines)

    if rng.random() < ENGAGEMENT["windfall_stone_chance"]:
        slo, shi = ENGAGEMENT["windfall_stone_range"]
        reward["spirit_stones"] = rng.randint(slo, shi)
        reward["message"] += f" Buried beneath your mat: {reward['spirit_stones']} spirit stones!"

    return reward


# ── Realm Milestone Titles ──────────────────────────────────────────

AUTO_TITLES = set(ENGAGEMENT["realm_titles"].values()) | {ENGAGEMENT["default_title"]}


def get_realm_title(realm: int) -> Optional[str]:
    return ENGAGEMENT["realm_titles"].get(realm)


def maybe_promote_title(current_title: str, new_realm: int) -> Tuple[str, bool]:
    """
    Auto-promote the Dao title on realm milestones, but never overwrite
    a player's custom title. Returns: (title, promoted)
    """
    new_title = get_realm_title(new_realm)
    if new_title and current_title in AUTO_TITLES:
        return new_title, True
    return current_title, False
