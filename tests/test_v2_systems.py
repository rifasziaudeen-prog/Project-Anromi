import pytest
import random
from datetime import datetime, timezone, timedelta

from core.balance import ROOTS, PHYSIQUES, SOUL, ENGAGEMENT
from services.root_engine import (
    roll_root,
    roll_physique,
    get_absorption_multiplier,
)
from services.engagement_engine import (
    update_streak,
    get_streak_multiplier,
    check_near_miss,
    maybe_windfall,
    maybe_promote_title,
    today_str,
)
from services.soul_engine import (
    resolve_death,
    compute_karmic_legacy,
    sync_remnant_vitality,
    calculate_possession_odds,
    execute_possession,
    calculate_reincarnation_benefits,
)
from services.cultivation_engine import (
    calculate_passive_energy_recovery,
    check_cultivation_deviation,
    execute_breakthrough,
)


# ── Roots ────────────────────────────────────────────────────────────

def test_root_gacha_covers_all_roots():
    rng = random.Random(42)
    seen = set()
    for _ in range(20000):
        name, purity = roll_root(rng=rng)
        seen.add(name)
        assert 0.0 <= purity <= 1.0
    assert seen == set(ROOTS.keys())

def test_root_luck_bonus_shifts_rarity():
    rng = random.Random(7)
    rare = {"Heaven Single-Element", "Mutant Lightning", "Mutant Wind", "Mutant Ice", "Mutant Space", "Divine Chaos"}
    lucky_hits = sum(1 for _ in range(5000) if roll_root(luck_bonus=0.5, rng=rng)[0] in rare)
    base_hits = sum(1 for _ in range(5000) if roll_root(luck_bonus=0.0, rng=rng)[0] in rare)
    assert lucky_hits > base_hits * 2

def test_absorption_multiplier_ordering():
    weak = get_absorption_multiplier("Mortal Five-Element", 0.4)
    strong = get_absorption_multiplier("Divine Chaos", 1.0)
    assert strong > weak * 8

def test_physique_roll_valid():
    rng = random.Random(1)
    names = set()
    for _ in range(2000):
        name, tier = roll_physique(rng=rng)
        names.add(name)
        assert PHYSIQUES[name]["tier"] == tier
    assert names == set(PHYSIQUES.keys())


# ── Engagement / Psychology ──────────────────────────────────────────

def test_streak_same_day_holds():
    now = datetime.now(timezone.utc)
    res = update_streak(today_str(now), 5, now=now)
    assert res["streak_days"] == 5
    assert res["changed"] is False

def test_streak_next_day_grows():
    now = datetime.now(timezone.utc)
    res = update_streak(today_str(now - timedelta(days=1)), 5, now=now)
    assert res["streak_days"] == 6
    assert res["changed"] is True

def test_streak_gap_resets():
    now = datetime.now(timezone.utc)
    res = update_streak(today_str(now - timedelta(days=4)), 9, now=now)
    assert res["streak_days"] == 1

def test_streak_multiplier_tiers():
    assert get_streak_multiplier(0) == 1.0
    assert get_streak_multiplier(3) == 1.10
    assert get_streak_multiplier(14) == 1.50
    assert get_streak_multiplier(99) == 2.00

def test_near_miss_detection():
    assert check_near_miss(roll=0.44, needed=0.45) is True
    assert check_near_miss(roll=0.10, needed=0.45) is False
    assert check_near_miss(roll=0.5, needed=0.0) is False

def test_windfall_with_forced_rng():
    class ForcedHigh(random.Random):
        def random(self):
            return 0.01  # always trigger
    wf = maybe_windfall(rng=ForcedHigh())
    assert wf is not None
    assert wf["insight"] >= ENGAGEMENT["windfall_insight_range"][0]

    class ForcedLow(random.Random):
        def random(self):
            return 0.99  # never trigger
    assert maybe_windfall(rng=ForcedLow()) is None

def test_title_promotion_respects_custom_titles():
    title, promoted = maybe_promote_title("Wandering Cultivator", 3)
    assert promoted and title == "Golden Core Sovereign"
    title, promoted = maybe_promote_title("MyCustomLegend", 3)
    assert not promoted and title == "MyCustomLegend"


# ── Soul Engine ──────────────────────────────────────────────────────

def test_true_death_below_nascent_soul():
    res = resolve_death(realm=3, highest_realm=3, total_breakthrough_wins=10)
    assert res["fate"] == "TRUE_DEATH"
    expected = SOUL["legacy_base"] + SOUL["legacy_per_realm"] * 2 + SOUL["legacy_per_breakthrough_win"] * 10
    assert res["legacy_awarded"] == expected

def test_remnant_soul_at_nascent_soul_and_above():
    res = resolve_death(realm=4, highest_realm=4, total_breakthrough_wins=20)
    assert res["fate"] == "REMNANT_SOUL"
    assert res["survived_as_soul"] is True
    assert res["vitality"] == 100.0

def test_vitality_decay_and_extinguish():
    since = datetime.now(timezone.utc) - timedelta(hours=10)
    res = sync_remnant_vitality(100.0, since)
    assert res["vitality"] == pytest.approx(100.0 - 10 * SOUL["vitality_decay_per_hour"], abs=0.5)
    assert res["extinguished"] is False

    ancient = datetime.now(timezone.utc) - timedelta(hours=1000)
    res = sync_remnant_vitality(100.0, ancient)
    assert res["vitality"] == 0.0
    assert res["extinguished"] is True

def test_possession_odds_bounds_and_scaling():
    weak = calculate_possession_odds(vitality=100.0, target_strength=1.0)["chance"]
    strong = calculate_possession_odds(vitality=100.0, target_strength=10.0)["chance"]
    assert 0.05 <= strong < weak <= 0.95

def test_possession_execution_seeded():
    res = execute_possession(100.0, 1.0, rng=random.Random(0))
    assert res["success"] is True or res["new_vitality"] < 100.0
    # vitality 20 - fail cost 25 -> extinguished on any failed attempt
    fail_case = [execute_possession(20.0, 10.0, rng=random.Random(i)) for i in range(50)]
    assert any(not r["success"] and r["extinguished"] for r in fail_case)

def test_reincarnation_benefits_scale_and_cap():
    zero = calculate_reincarnation_benefits(0)
    assert zero["tokens_spent"] == 0 and zero["root_luck_bonus"] == 0.0

    huge = calculate_reincarnation_benefits(999999)
    assert huge["root_luck_bonus"] == SOUL["reincarnation_luck_cap"]
    assert huge["starting_stone_bonus"] == SOUL["reincarnation_stones_cap"]

    mid = calculate_reincarnation_benefits(50)  # below both caps
    assert mid["root_luck_bonus"] == pytest.approx(50 * SOUL["reincarnation_luck_per_token"])
    assert mid["starting_stone_bonus"] == 100


# ── Deviation & Permadeath Hooks ─────────────────────────────────────

def test_deviation_never_triggers_above_threshold():
    assert check_cultivation_deviation(80.0, rng=random.Random()) is None

def test_deviation_can_trigger_below_threshold():
    triggered = any(
        check_cultivation_deviation(5.0, rng=random.Random(i)) is not None
        for i in range(200)
    )
    assert triggered

def test_total_meridian_rupture_flags_body_destroyed():
    # Force catastrophic outcome by seeding rolls until severity CATASTROPHIC fires
    destroyed_found = False
    for seed in range(400):
        rng_state = random.getstate()
        random.seed(seed)
        res = execute_breakthrough(
            realm=1, stage="Layer 6",
            current_energy=100.0, max_energy=100.0,
            meridian_damage=0.5, qi_purity=0.5
        )
        random.setstate(rng_state)
        if res.get("body_destroyed"):
            destroyed_found = True
            assert res["is_dead"] is True
            break
    assert destroyed_found

def test_passive_recovery_accepts_physique_bonus():
    t_prev = datetime.now(timezone.utc) - timedelta(minutes=30)
    _, base = calculate_passive_energy_recovery(
        current_energy=10.0, max_energy=100.0, last_meditated=t_prev,
        realm=1, stage="Layer 1"
    )
    _, boosted = calculate_passive_energy_recovery(
        current_energy=10.0, max_energy=100.0, last_meditated=t_prev,
        realm=1, stage="Layer 1", physique_absorption_bonus=0.35
    )
    assert boosted > base
