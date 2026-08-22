import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from models.realm import (
    RealmTier,
    REALM_METADATA,
    get_realm_meta,
    get_stages_for_realm,
    is_bottleneck_stage,
    NINE_LAYERS_STAGES,
    FOUR_STAGES_LIST
)
from services.cultivation_engine import (
    calculate_passive_energy_recovery,
    calculate_breakthrough_odds,
    execute_breakthrough
)

def test_16_realms_structure():
    """Verify all 16 realms are present and correctly configured."""
    assert len(REALM_METADATA) == 16

    # Realms 1 to 8 must have 9 layers + Great Circle (10 sub-stages)
    for r in range(1, 9):
        stages = get_stages_for_realm(r)
        assert len(stages) == 10
        assert stages == NINE_LAYERS_STAGES

    # Realms 9 to 15 (True Immortal to Sovereign) must have 4 sub-stages (Early, Mid, Late, Peak)
    for r in range(9, 16):
        stages = get_stages_for_realm(r)
        assert len(stages) == 4
        assert stages == FOUR_STAGES_LIST

    # Realm 16 (Eternal Transcendent)
    r16_stages = get_stages_for_realm(16)
    assert len(r16_stages) == 1
    assert r16_stages[0] == "Absolute Perfection"

def test_bottleneck_recognition():
    """Verify bottleneck identification across 9-layer and 4-stage realms."""
    # 9-layer realms: Layer 3, 6, 9, Great Circle
    assert is_bottleneck_stage(1, "Layer 3") is True
    assert is_bottleneck_stage(1, "Layer 4") is False
    assert is_bottleneck_stage(1, "Layer 6") is True
    assert is_bottleneck_stage(1, "Layer 9") is True
    assert is_bottleneck_stage(1, "Great Circle") is True

    # 4-stage realms: All are bottleneck stages
    assert is_bottleneck_stage(9, "Early Stage") is True
    assert is_bottleneck_stage(9, "Middle Stage") is True
    assert is_bottleneck_stage(9, "Peak Stage") is True

def test_passive_qi_absorption():
    """Verify passive Qi gathering with diminishing returns."""
    t_prev = datetime.now(timezone.utc) - timedelta(minutes=30)
    current_qi = 10.0
    max_qi = 100.0

    new_qi, gathered = calculate_passive_energy_recovery(
        current_energy=current_qi,
        max_energy=max_qi,
        last_meditated=t_prev,
        realm=1,
        stage="Layer 1",
        root="Heaven Single-Element",
        root_purity=0.95
    )

    assert new_qi > current_qi
    assert gathered > 0
    assert new_qi <= max_qi

def test_breakthrough_odds_insufficient_qi():
    """Verify breakthrough is blocked below 85% Qi."""
    odds = calculate_breakthrough_odds(
        realm=1,
        stage="Layer 1",
        current_energy=50.0,
        max_energy=100.0
    )
    assert odds["can_attempt"] is False
    assert odds["final_chance"] == 0.0

def test_breakthrough_odds_sufficient_qi():
    """Verify breakthrough odds calculation when Qi >= 85%."""
    odds = calculate_breakthrough_odds(
        realm=1,
        stage="Layer 1",
        current_energy=95.0,
        max_energy=100.0,
        qi_purity=0.80
    )
    assert odds["can_attempt"] is True
    assert 0.05 <= odds["final_chance"] <= 0.98

def test_breakthrough_execution():
    """Verify breakthrough execution returns valid outcomes."""
    res = execute_breakthrough(
        realm=1,
        stage="Layer 1",
        current_energy=100.0,
        max_energy=100.0,
        qi_purity=0.90
    )
    assert res["outcome"] in ["SUCCESS", "FAILURE"]
    assert res["current_energy"] <= res["max_energy"]
