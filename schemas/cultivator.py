from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List

class CultivatorRegister(BaseModel):
    discord_id: str
    username: str
    dao_title: Optional[str] = "Wandering Cultivator"

class CultivatorProfileResponse(BaseModel):
    id: int
    discord_id: str
    username: str
    dao_title: str

    # 16-Realm Cultivation Status
    realm: int
    realm_name_en: str
    realm_name_cn: str
    stage: str
    is_bottleneck: bool

    # Meridian & Spiritual Qi State
    spirit_energy: float
    max_energy: float
    qi_purity: float
    meridian_damage: float

    # Longevity
    lifespan_current_years: float
    lifespan_max_years: float

    # Dao Heart & Karma
    dao_heart_stability: float
    karma_sin: int

    # Talents
    spiritual_root: str
    spiritual_root_purity: float
    physique_tier: int
    physique_name: str

    # Permadeath & Remnant Soul State
    is_dead: bool
    is_remnant_soul: bool
    soul_state: str = "ALIVE"
    remnant_soul_vitality: float
    lineage_generation: int = 1
    death_count: int = 0
    karmic_legacy_tokens: int

    # Engagement & Progress
    streak_days: int = 0
    best_streak: int = 0
    dao_insight: int = 0
    highest_realm_achieved: int = 1
    total_meditations: int = 0
    total_breakthrough_wins: int = 0
    total_breakthrough_fails: int = 0

    # Economy
    spirit_stones: int

    # Crafting & Alchemy state
    luck_stat: int = 5
    pill_toxicity: float = 0.0
    stored_breakthrough_bonus: float = 0.0
    alchemy_level: int = 1
    alchemy_title: Optional[str] = None
    forging_level: int = 1
    forging_title: Optional[str] = None

    last_meditated: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class MeditateResponse(BaseModel):
    message: str
    qi_gathered: float
    spirit_energy: float
    max_energy: float
    is_full: bool
    can_breakthrough: bool
    meridian_damage: float
    # Engagement extensions
    streak_days: int = 0
    streak_multiplier: float = 1.0
    dao_insight_gained: int = 0
    deviation_triggered: bool = False
    windfall: Optional[Dict[str, Any]] = None

class BreakthroughOddsResponse(BaseModel):
    can_attempt: bool
    is_bottleneck: bool
    is_realm_leap: bool
    base_chance: float
    modifiers: Dict[str, float]
    final_chance: float
    target_realm: int
    target_stage: str
    reason: Optional[str] = None

class BreakthroughRequest(BaseModel):
    pill_bonus: Optional[float] = 0.0

class BreakthroughResultResponse(BaseModel):
    success: bool
    outcome: str
    message: str
    roll: Optional[float] = None
    needed: Optional[float] = None
    realm: int
    realm_name_en: str
    realm_name_cn: str
    stage: str
    spirit_energy: float
    max_energy: float
    dao_heart: float
    meridian_damage: float
    is_dead: bool
    is_remnant_soul: bool
    # Extensions
    near_miss: bool = False
    body_destroyed: bool = False
    soul_fate: Optional[str] = None
    karmic_legacy_awarded: int = 0
    title_promoted: bool = False

# ── Dao Heart ────────────────────────────────────────────────────────

class DaoHeartResponse(BaseModel):
    discord_id: str
    dao_heart_stability: float
    status: str
    deviation_risk_chance: float
    deviation_threshold: float
    karma_sin: int
    karma_class: str
    message: str

# ── Soul / Permadeath ────────────────────────────────────────────────

class PossessRequest(BaseModel):
    target_name: str = "Nameless Mortal"
    target_strength: float = Field(default=3.0, ge=1.0, le=10.0)

class SoulStateResponse(BaseModel):
    discord_id: str
    soul_state: str
    is_dead: bool
    is_remnant_soul: bool
    remnant_soul_vitality: float
    hours_as_soul: float
    karmic_legacy_tokens: int
    lineage_generation: int
    death_count: int
    message: str

class ReincarnateResponse(BaseModel):
    message: str
    tokens_spent: int
    root_luck_bonus: float
    starting_stone_bonus: int
    lineage_generation: int
    profile: CultivatorProfileResponse
