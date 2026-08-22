import pytest
import random
import statistics
from datetime import datetime, timezone, timedelta

from core.balance import (
    ALCHEMY, FORGING, ECONOMY, GATHERING, PILL_RECIPES, ARTIFACTS,
    FURNACES, FLAMES, MINERALS, ITEMS_REGISTRY,
)
from services.alchemy_engine import (
    grade_from_impurity,
    compute_impurity,
    consumption_toxicity,
    grade_potency,
    apply_recipe_effects,
    xp_gain,
    level_from_exp,
)
from services.forging_engine import (
    calculate_success_chance,
    attempt_forge,
    xp_to_level,
)
from services.economy_engine import (
    convert_stones, plan_charge, daily_stock, merchant_seed, buy_price, sell_price
)
from services.gathering_engine import gather_cooldown_remaining, _age_tier_weights


# ── Impurity-Driven Grades ───────────────────────────────────────────

def test_grade_mapping_thresholds():
    assert grade_from_impurity(0.0) == "Flawless"
    assert grade_from_impurity(0.99) == "Flawless"
    assert grade_from_impurity(5.0) == "Top"
    assert grade_from_impurity(10.0) == "Top"
    assert grade_from_impurity(20.0) == "Medium"
    assert grade_from_impurity(32.0) == "Medium"
    assert grade_from_impurity(45.0) == "Low"
    assert grade_from_impurity(100.0) == "Low"

def test_mastery_lowers_impurity_center():
    rng = random.Random(11)
    recipe = PILL_RECIPES["core_condensation_pill"]  # base_impurity 58
    novice = statistics.mean(
        compute_impurity(recipe, 0, 0, 1, 5, rng)["impurity"] for _ in range(400)
    )
    master = statistics.mean(
        compute_impurity(recipe, 0, 0, 8, 5, rng)["impurity"] for _ in range(400)
    )
    assert master < novice - 15

def test_mastery_narrows_randomness():
    rng = random.Random(23)
    recipe = PILL_RECIPES["qi_gathering_pill"]
    novice_spread = statistics.pstdev(
        compute_impurity(recipe, 0, 0, 1, 5, rng)["impurity"] for _ in range(500)
    )
    master_spread = statistics.pstdev(
        compute_impurity(recipe, 0, 0, 9, 5, rng)["impurity"] for _ in range(500)
    )
    assert master_spread < novice_spread

def test_pure_luck_cannot_flawless_hard_pills():
    """A Tier-4 pill at Mastery 1 must stay out of Flawless even at Luck 100."""
    rng = random.Random(31)
    recipe = PILL_RECIPES["nascent_soul_formation_pill"]  # base_impurity 68
    flawless = sum(
        1 for _ in range(300)
        if compute_impurity(recipe, 0, 0, 1, 100, rng)["grade"] == "Flawless"
    )
    assert flawless == 0

def test_mastery_plus_good_gear_reaches_flawless():
    rng = random.Random(47)
    recipe = PILL_RECIPES["qi_gathering_pill"]
    best_furnace = FURNACES["furnace_primordial_chaos"]["impurity_reduction"]
    best_flame = FLAMES["flame_celestial_spirit"]["impurity_reduction"]
    grades = [
        compute_impurity(recipe, best_furnace, best_flame, 10, 30, rng)["grade"]
        for _ in range(300)
    ]
    assert "Flawless" in grades and "Top" in grades

def test_toxicity_zero_on_flawless_positive_on_low():
    assert consumption_toxicity("Flawless") == 0.0
    assert consumption_toxicity("Low") > consumption_toxicity("Medium") > consumption_toxicity("Top") > 0

def test_potency_and_effects_scale_by_grade():
    assert grade_potency("Flawless") > grade_potency("Top") > grade_potency("Medium") > grade_potency("Low")
    recipe = PILL_RECIPES["foundation_establishment_pill"]
    low_fx = apply_recipe_effects(recipe, "Low")
    flaw_fx = apply_recipe_effects(recipe, "Flawless")
    assert flaw_fx["breakthrough_bonus"] > low_fx["breakthrough_bonus"]

def test_xp_scales_with_grade_and_curve_monotonic():
    assert xp_gain(PILL_RECIPES["qi_gathering_pill"], "Flawless") > xp_gain(PILL_RECIPES["qi_gathering_pill"], "Low")
    curve = ALCHEMY["xp_curve"]
    assert all(curve[i] < curve[i + 1] for i in range(len(curve) - 1))

def test_level_progression_boundaries():
    curve = ALCHEMY["xp_curve"]
    fresh = level_from_exp(0)
    assert fresh["level"] == 1
    mid = level_from_exp(curve[3])
    assert mid["level"] == 4
    maxed = level_from_exp(999999)
    assert maxed["level"] == len(curve)


# ── Forging ──────────────────────────────────────────────────────────

def test_forging_success_scales_with_level_and_tier():
    mortal_low = calculate_success_chance(ARTIFACTS["weapon_mortal"], 1)
    mortal_high = calculate_success_chance(ARTIFACTS["weapon_mortal"], 10)
    primordial_high = calculate_success_chance(ARTIFACTS["weapon_primordial"], 10)
    assert mortal_high > mortal_low
    assert primordial_high < mortal_high

def test_forge_failure_consumes_half_materials():
    rng = random.Random(5)
    artifact = ARTIFACTS["armor_magical"]
    results = [attempt_forge(artifact, 1, rng=rng) for _ in range(60)]
    fails = [r for r in results if not r["success"]]
    assert fails, "expected at least one failure in 60 attempts"
    for f in fails:
        for mat_id, orig_qty in artifact["materials"].items():
            lost = f["lost_materials"][mat_id]
            assert 1 <= lost <= orig_qty * FORGING["fail_material_loss_ratio"] + 0.51
    successes = [r for r in results if r["success"]]
    for s in successes:
        assert s["lost_materials"] == {}

def test_forging_level_curve():
    assert xp_to_level(0)["level"] == 1
    assert xp_to_level(FORGING["xp_curve"][2])["level"] == 3


# ── Economy ──────────────────────────────────────────────────────────

def test_stone_conversion_math():
    ok, units, msg = convert_stones(250, "up")
    assert ok and units == 2
    ok, lows, _ = convert_stones(3, "down")
    assert ok and lows == 300
    ok, _, _ = convert_stones(50, "up")
    assert not ok

def test_plan_charge_auto_breaks_higher_grades():
    # Wallet empty, 1 mid-grade stone, cost 150 -> breaks mid into 100, still short -> needs another source
    plan = plan_charge(low_wallet=50, mid_count=1, high_count=0, top_count=0, cost=150)
    assert plan["ok"]
    assert plan["mid_delta"] == -1
    assert plan["change_low"] == 0 or plan["change_low"] >= 0

def test_plan_charge_insufficient_funds():
    plan = plan_charge(low_wallet=10, mid_count=0, high_count=0, top_count=0, cost=999999)
    assert not plan["ok"]

def test_merchant_stock_deterministic_per_day():
    d1a = daily_stock("2026-08-21", realm_gate=16)
    d1b = daily_stock("2026-08-21", realm_gate=16)
    assert d1a == d1b
    assert len(d1a) == ECONOMY["merchant_daily_slots"]

def test_merchant_rotates_across_days():
    seen = set()
    for day in range(1, 15):
        stock = daily_stock(f"2026-09-{day:02d}", realm_gate=16)
        seen.add(tuple(s["item_id"] for s in stock))
    assert len(seen) > 1  # rotation actually happens

def test_merchant_respects_realm_gate():
    low_realm_stock = daily_stock("2026-08-21", realm_gate=1)
    allowed_ids = {e["item_id"] for e in __import__("core.balance", fromlist=["MERCHANT_STOCK_POOL"]).MERCHANT_STOCK_POOL if e["min_realm"] <= 1}
    assert all(s["item_id"] in allowed_ids for s in low_realm_stock)

def test_buy_sell_prices_sane():
    assert buy_price("flame_wood") > sell_price("flame_wood")
    top_sell = sell_price("nascent_soul_formation_pill", "Flawless")
    low_sell = sell_price("nascent_soul_formation_pill", "Low")
    assert top_sell > low_sell


# ── Gathering ────────────────────────────────────────────────────────

def test_gather_cooldown():
    now = datetime.now(timezone.utc)
    assert gather_cooldown_remaining(None, now) == 0.0
    recent = now - timedelta(minutes=5)
    remaining = gather_cooldown_remaining(recent, now)
    assert GATHERING["cooldown_minutes"] - 6 < remaining <= GATHERING["cooldown_minutes"] - 4
    ancient = now - timedelta(hours=5)
    assert gather_cooldown_remaining(ancient, now) == 0.0

def test_age_weights_shift_toward_old_growth_with_realm():
    young = _age_tier_weights(1)
    elder = _age_tier_weights(16)
    assert elder[3] > young[3]          # 10k-year herbs get weight from realm
    assert elder[0] <= young[0]         # common tier never grows
    # Relative share of the oldest tier must rise (choices() normalizes sums)
    young_share = young[3] / sum(young)
    elder_share = elder[3] / sum(elder)
    assert elder_share > young_share * 2


# ── Registry integrity ───────────────────────────────────────────────

def test_all_recipe_materials_exist_in_registry():
    for rid, recipe in PILL_RECIPES.items():
        for mat_id in recipe["materials"]:
            assert mat_id in ITEMS_REGISTRY, f"{rid} references unknown material {mat_id}"

def test_all_artifact_materials_exist():
    for aid, art in ARTIFACTS.items():
        for mat_id in art["materials"]:
            assert mat_id in ITEMS_REGISTRY, f"{aid} references unknown material {mat_id}"

def test_all_merchant_pool_items_exist():
    for entry in __import__("core.balance", fromlist=["MERCHANT_STOCK_POOL"]).MERCHANT_STOCK_POOL:
        assert entry["item_id"] in ITEMS_REGISTRY
