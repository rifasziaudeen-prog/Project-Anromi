import pytest
import random
from core.balance import (
    TRIBULATION, WORLD, WORLD_NODES, ENCOUNTERS, ENCOUNTER_TUNING,
    ARTIFACTS, get_root_config,
)
from services.tribulation_engine import (
    select_tier,
    build_tribulation,
    resolve_wave,
    serialize_state,
    deserialize_state,
    near_miss_death,
    tribulation_summary,
    compute_t_score,
)
from services.world_engine import (
    are_connected,
    travel_cost,
    roll_encounter,
    _encounter_weights,
    resolve_cave_gamble,
    resolve_ambush,
    compute_player_power,
)


# ── Tribulation tier selection ───────────────────────────────────────

def test_tier_selection_by_karma_and_talent():
    assert select_tier("Mortal Five-Element", 0) == ("FOUR_NINE", 36)
    assert select_tier("Heaven Single-Element", 0)[0] == "SIX_NINE"      # Epic rarity
    assert select_tier("Mutant Lightning", 0)[0] == "SIX_NINE"           # Legendary
    assert select_tier("Divine Chaos", 0) == ("NINE_NINE", 81)           # heaven-defying root
    assert select_tier("Mortal Five-Element", 650) == ("NINE_NINE", 81)  # great sin
    assert select_tier("True Three-Element", 350)[0] == "SIX_NINE"       # moderate sin


# ── Build & structure ────────────────────────────────────────────────

def _base_kwargs(**over):
    kw = dict(
        target_realm=4,
        spiritual_root="Mortal Five-Element",
        karma_sin=0,
        spirit_energy=1000.0,
        max_energy=50000.0,
        physique_tier=1,
        physique_resistance=0.10,
        luck_stat=5,
        dao_heart=90.0,
        equipped={"weapon": None, "armor": None, "banner": None},
        stage_index=4,
    )
    kw.update(over)
    return kw

def test_build_waves_sum_to_total():
    state = build_tribulation(**_base_kwargs())
    assert sum(w["strikes"] for w in state["_waves"]) == state["total_strikes"]
    assert len(state["_waves"]) == 4
    assert state["qi_pool"] == 1000.0
    assert state["body_pool"] == pytest.approx(50000 * TRIBULATION["body_pool_factor"])

def test_build_snapshots_gear_power():
    art = ARTIFACTS["weapon_spirit"]
    state = build_tribulation(**_base_kwargs(equipped={"weapon": art, "armor": None, "banner": None}))
    assert state["gear"]["weapon"]["power_left"] == art["power"]
    assert state["gear"]["armor"] is None


# ── Wave resolution ──────────────────────────────────────────────────

def test_endure_first_wave_ongoing():
    state = build_tribulation(**_base_kwargs())
    res = resolve_wave(state, "endure", rng=random.Random(3))
    assert res["outcome"] == "ONGOING"
    assert state["wave_index"] == 1
    assert state["strikes_done_total"] == state["_waves"][0]["strikes"]

def test_sacrifice_nullifies_wave_damage():
    art = ARTIFACTS["weapon_mortal"]
    state = build_tribulation(**_base_kwargs(equipped={"weapon": art, "armor": None, "banner": None}))
    qi_before = state["qi_pool"]
    body_before = state["body_pool"]
    res = resolve_wave(state, "sacrifice:weapon", rng=random.Random(5))
    assert res["outcome"] == "ONGOING"
    assert state["gear"]["weapon"] is None
    assert state["qi_pool"] == pytest.approx(qi_before)
    assert state["body_pool"] == pytest.approx(body_before)

def test_shield_absorbs_before_pools():
    state = build_tribulation(**_base_kwargs(spirit_energy=0.0))
    state["shield"] = 999999.0
    body_before = state["body_pool"]
    resolve_wave(state, "endure", rng=random.Random(7))
    assert state["shield"] < 999999.0
    assert state["body_pool"] == pytest.approx(body_before)

def test_weak_cultivator_is_destroyed():
    # No gear, no qi, tiny body pool vs a realm-16 storm → quick death
    state = build_tribulation(**_base_kwargs(
        target_realm=16, spirit_energy=0.0, max_energy=100.0,
        physique_tier=0, physique_resistance=0.0,
    ))
    outcome = None
    for _ in range(6):
        res = resolve_wave(state, "endure", rng=random.Random(11))
        outcome = res["outcome"]
        if outcome in ("DESTROYED", "SURVIVED"):
            break
    assert outcome == "DESTROYED"

def test_strong_prepared_cultivator_survives_four_nine():
    # Realm-3 peak cultivator with top gear crossing into realm 4
    arts = {s: ARTIFACTS[f"{s}_dao"] for s in ("weapon", "armor", "banner")}
    state = build_tribulation(**_base_kwargs(
        target_realm=4, spirit_energy=7000.0, max_energy=8000.0,
        physique_tier=3, physique_resistance=0.40, luck_stat=40,
        dao_heart=95.0, equipped=arts, stage_index=9,
    ))
    outcome = None
    for _ in range(6):
        res = resolve_wave(state, "endure", rng=random.Random(13))
        outcome = res["outcome"]
        if outcome != "ONGOING":
            break
    assert outcome == "SURVIVED"

def test_heart_demon_drains_dao_heart_and_can_kill():
    state = build_tribulation(**_base_kwargs(dao_heart=5.0))
    # Fast-forward to the final wave
    while state["wave_index"] < len(state["_waves"]) - 1:
        resolve_wave(state, "endure", rng=random.Random(17))
    res = resolve_wave(state, "endure", rng=random.Random(19))
    if res["outcome"] == "DESTROYED":
        assert state["dao_heart"] <= 0
    else:
        assert state["dao_heart"] > 0 or res["outcome"] == "SURVIVED"

def test_bail_ends_without_death():
    state = build_tribulation(**_base_kwargs())
    res = resolve_wave(state, "bail")
    assert res["outcome"] == "BAILED"

def test_invalid_sacrifice_rejected():
    state = build_tribulation(**_base_kwargs())
    res = resolve_wave(state, "sacrifice:weapon", rng=random.Random(2))
    assert res["outcome"] == "INVALID"


# ── Serialization & helpers ──────────────────────────────────────────

def test_state_serialization_roundtrip():
    state = build_tribulation(**_base_kwargs())
    raw = serialize_state(state)
    restored = deserialize_state(raw)
    assert restored["total_strikes"] == state["total_strikes"]
    assert restored["_waves"] == state["_waves"]

def test_near_miss_detection():
    state = build_tribulation(**_base_kwargs())
    state["strikes_done_total"] = state["total_strikes"] - 1
    assert near_miss_death(state) is True
    state["strikes_done_total"] = 3
    assert near_miss_death(state) is False

def test_summary_shape():
    s = tribulation_summary(build_tribulation(**_base_kwargs()))
    for key in ("target_realm", "tier", "total_strikes", "waves_remaining", "gear"):
        assert key in s


# ── World graph ──────────────────────────────────────────────────────

def test_graph_connections_reference_existing_nodes():
    for node_id, node in WORLD_NODES.items():
        for conn in node["connections"]:
            assert conn in WORLD_NODES, f"{node_id} -> unknown {conn}"

def test_adjacency_symmetric_in_balance_seed():
    # The migrator symmetrizes; balance itself should already be symmetric
    for node_id, node in WORLD_NODES.items():
        for conn in node["connections"]:
            assert node_id in WORLD_NODES[conn]["connections"], f"{conn} does not link back to {node_id}"

def test_are_connected():
    assert are_connected("sect_valley", "azure_river_dock")
    assert not are_connected("sect_valley", "volcanic_crown")

def test_travel_cost_scales_with_danger():
    cheap = travel_cost("sect_valley", "azure_river_dock")[1]
    pricey = travel_cost("pearl_atoll", "sunken_ruin_shoals")[1]
    assert pricey > cheap


# ── Encounters ───────────────────────────────────────────────────────

def test_danger_shifts_encounter_weights():
    low = dict(_encounter_weights(1))
    high = dict(_encounter_weights(12))
    assert high["ambush"] > low["ambush"]
    assert high["ancient_cave"] > low["ancient_cave"]
    assert high["herb_find"] < low["herb_find"]

def test_roll_encounter_returns_known_types():
    rng = random.Random(9)
    seen = set()
    for _ in range(300):
        seen.add(roll_encounter({"danger_tier": 6}, rng))
    assert seen.issubset(set(ENCOUNTERS.keys()))
    assert len(seen) >= 3

def test_cave_gamble_bounds():
    rng = random.Random(21)
    results = [resolve_cave_gamble(8, 50, rng=rng) for _ in range(80)]
    wins = [r for r in results if r["success"]]
    losses = [r for r in results if not r["success"]]
    assert wins and losses
    for w in wins:
        assert w["insight"] >= ENCOUNTER_TUNING["cave_reward_insight_range"][0]
        assert w["stones"] > 0
    for l in losses:
        assert l["meridian_damage"] > 0

def test_ambush_outcomes_bounded():
    rng = random.Random(33)
    strong = compute_player_power(realm=8, stage_index=5, equipped_artifact_powers=480,
                                  physique_tier=3, luck_stat=30)
    results = {resolve_ambush(strong, 3, 1000, "fight", rng=rng)["result"] for _ in range(60)}
    assert "VICTORY" in results
    weak_results = [resolve_ambush(5.0, 12, 500, "fight", rng=rng) for _ in range(40)]
    assert any(r["result"] == "DEFEAT" for r in weak_results)
    flee = [resolve_ambush(5.0, 2, 500, "flee", rng=rng) for _ in range(40)]
    assert any(r["result"] == "ESCAPED" for r in flee)
