"""
Soul Engine (Canhun) — Hardcore permadeath, Remnant Soul survival,
possession (Duo She), and karmic reincarnation.
All tunables live in core/balance.py → SOUL.
"""
import random
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from core.balance import SOUL


# ── Death Resolution ────────────────────────────────────────────────

def compute_karmic_legacy(highest_realm: int, total_breakthrough_wins: int) -> int:
    """Legacy points awarded to the lineage when a cultivator truly dies."""
    return (
        SOUL["legacy_base"]
        + SOUL["legacy_per_realm"] * max(0, highest_realm - 1)
        + SOUL["legacy_per_breakthrough_win"] * max(0, total_breakthrough_wins)
    )


def resolve_death(realm: int, highest_realm: int, total_breakthrough_wins: int) -> Dict[str, Any]:
    """
    The single source of truth for what happens when a body is destroyed.
    Realm < Nascent Soul → TRUE DEATH (lineage continues via reincarnation).
    Realm >= Nascent Soul → REMNANT SOUL state with a decaying vitality timer.
    """
    if realm >= SOUL["remnant_min_realm"]:
        return {
            "fate": "REMNANT_SOUL",
            "survived_as_soul": True,
            "vitality": 100.0,
            "legacy_awarded": 0,
            "message": (
                "💀 Your body is OBLITERATED... but your Nascent Soul tears free from the wreckage, "
                "screaming into the night sky! You are now a REMNANT SOUL — find a vessel before "
                "your soul-fire extinguishes!"
            ),
        }
    legacy = compute_karmic_legacy(highest_realm, total_breakthrough_wins)
    return {
        "fate": "TRUE_DEATH",
        "survived_as_soul": False,
        "vitality": 0.0,
        "legacy_awarded": legacy,
        "message": (
            f"☠️ Your meridians detonated beyond repair. With a final cry, your Qi scatters to the "
            f"heavens... TRUE DEATH. But your deeds echo in karma: {legacy} Karmic Legacy tokens "
            f"pass to your next incarnation."
        ),
    }


# ── Remnant Soul Vitality Decay ─────────────────────────────────────

def sync_remnant_vitality(
    vitality: float,
    soul_since: Optional[datetime],
    now: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Lazily applies decay since the soul left its body.
    Returns updated vitality and whether the soul has fully extinguished.
    """
    now = now or datetime.now(timezone.utc)
    if soul_since is None:
        return {"vitality": vitality, "extinguished": vitality <= 0, "hours_elapsed": 0.0}

    if soul_since.tzinfo is None:
        soul_since = soul_since.replace(tzinfo=timezone.utc)

    hours = max(0.0, (now - soul_since).total_seconds() / 3600.0)
    new_vitality = max(0.0, vitality - hours * SOUL["vitality_decay_per_hour"])
    return {
        "vitality": round(new_vitality, 2),
        "extinguished": new_vitality <= 0,
        "hours_elapsed": round(hours, 2),
    }


# ── Possession (Duo She) ────────────────────────────────────────────

def calculate_possession_odds(vitality: float, target_strength: float) -> Dict[str, Any]:
    """
    Odds of forcibly seizing a mortal vessel.
    target_strength: 1 (dying beggar) to 10 (peak mortal martial master).
    Stronger wills resist; weaker souls burn out faster.
    """
    chance = (
        SOUL["possession_base_chance"]
        + vitality * SOUL["possession_vitality_bonus_scale"]
        - target_strength * SOUL["possession_strength_penalty"]
    )
    chance = max(0.05, min(0.95, chance))
    return {
        "chance": round(chance, 4),
        "base": SOUL["possession_base_chance"],
        "vitality_bonus": round(vitality * SOUL["possession_vitality_bonus_scale"], 4),
        "strength_penalty": round(target_strength * SOUL["possession_strength_penalty"], 4),
    }


def execute_possession(vitality: float, target_strength: float, rng: Optional[random.Random] = None) -> Dict[str, Any]:
    """Resolves a possession attempt. Failure burns soul vitality."""
    rng = rng or random
    odds = calculate_possession_odds(vitality, target_strength)
    roll = rng.random()
    success = roll <= odds["chance"]

    if success:
        return {
            "success": True,
            "roll": round(roll, 4),
            "odds": odds["chance"],
            "karma_gain": SOUL["possession_success_karma"],
            "new_vitality": 100.0,
            "message": (
                "👹 Your soul LUNGES into the mortal vessel! The original spirit shrieks and is "
                "crushed beneath your will. Flesh again... but Heaven has marked this sin."
            ),
        }
    remaining = max(0.0, vitality - SOUL["possession_fail_vitality_cost"])
    return {
        "success": False,
        "roll": round(roll, 4),
        "odds": odds["chance"],
        "karma_gain": SOUL["possession_fail_karma"],
        "new_vitality": round(remaining, 2),
        "extinguished": remaining <= 0,
        "message": (
            "⚡ The vessel's soul resisted FIERCELY! You were violently expelled, your soul-form "
            "torn and flickering. Vitality drains away..."
        ),
    }


# ── Reincarnation ───────────────────────────────────────────────────

def calculate_reincarnation_benefits(karmic_tokens: int) -> Dict[str, Any]:
    """
    Spends all Karmic Legacy tokens on the next life:
    rare-root luck, starting wealth, and past-life insight retention.
    """
    tokens = max(0, karmic_tokens)
    luck = min(SOUL["reincarnation_luck_cap"], tokens * SOUL["reincarnation_luck_per_token"])
    stones = min(SOUL["reincarnation_stones_cap"], tokens * SOUL["reincarnation_stones_per_token"])
    return {
        "tokens_spent": tokens,
        "root_luck_bonus": round(luck, 4),
        "starting_stone_bonus": stones,
        "comprehension_retention_pct": SOUL["reincarnation_comprehension_retention"],
        "message": (
            f"☸️ {tokens} Karmic Legacy tokens dissolve into the wheel of rebirth. "
            f"Your next incarnation stirs in a distant village... with fate subtly bent in its favor."
        ) if tokens > 0 else "☸️ You have no karmic legacy. You are reborn as nameless mortals are — bare and forgotten.",
    }
