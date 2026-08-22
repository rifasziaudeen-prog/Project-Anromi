from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List


# ── World ────────────────────────────────────────────────────────────

class NodeInfo(BaseModel):
    id: str
    name: str
    region: str
    plane: str
    spirit_density: float
    elemental_bias: str
    danger_tier: int
    description: str

class NeighborNode(BaseModel):
    id: str
    name: str
    region: str
    danger_tier: int
    travel_cooldown_minutes: float
    qi_cost_pct: float

class MapResponse(BaseModel):
    discord_id: str
    current_node: NodeInfo
    neighbors: List[NeighborNode]
    travel_locked_until: Optional[datetime] = None
    message: str

class TravelRequest(BaseModel):
    target_node_id: str

class TravelResponse(BaseModel):
    success: bool
    message: str
    current_node_id: str
    arrival_unlock_at: Optional[datetime] = None

class ExploreRequest(BaseModel):
    ambush_choice: Optional[str] = None   # "fight" | "flee"; auto-picked when omitted

class ExploreResponse(BaseModel):
    encounter: str                        # HERB/MINERAL/CARAVAN/CAVE/AMBUSH/NOTHING
    message: str
    details: Dict[str, Any] = {}
    cooldown_minutes: float

# ── Tribulation ──────────────────────────────────────────────────────

class TribulationSummaryModel(BaseModel):
    target_realm: int
    tier: str
    total_strikes: int
    strikes_endured: int
    waves_remaining: int
    qi_pool: float
    body_pool: float
    shield: float
    dao_heart: float
    meridian_damage: float
    gear: Dict[str, Optional[str]]

class TribulationStateResponse(BaseModel):
    active: bool
    summary: Optional[TribulationSummaryModel] = None
    log_tail: List[str] = []
    message: str

class TribulationActionRequest(BaseModel):
    action: str   # "endure" | "sacrifice:<weapon|armor|banner>" | "pill" | "bail"

class TribulationActionResponse(BaseModel):
    outcome: str                         # ONGOING / SURVIVED / DESTROYED / BAILED / INVALID
    events: List[str]
    summary: Optional[TribulationSummaryModel] = None
    realm_advanced_to: Optional[int] = None
    soul_fate: Optional[str] = None
    karmic_legacy_awarded: int = 0
    destroyed_artifacts: List[str] = []
