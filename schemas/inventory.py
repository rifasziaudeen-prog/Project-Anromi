from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List


# ── Inventory ────────────────────────────────────────────────────────

class BagEntry(BaseModel):
    item_id: str
    name: str
    category: str
    quality: Optional[str] = None
    quantity: int
    base_price: int = 0

class BagResponse(BaseModel):
    discord_id: str
    spirit_stones: int          # low-grade wallet
    pill_toxicity: float
    entries: List[BagEntry]
    message: str

class ConsumeRequest(BaseModel):
    item_id: str
    quality: Optional[str] = None   # exact grade; default burns lowest first

class ConsumeResponse(BaseModel):
    success: bool
    message: str
    effects_applied: Dict[str, Any] = {}
    toxicity_gained: float = 0.0
    pill_toxicity: float = 0.0

# ── Gathering ────────────────────────────────────────────────────────

class GatherResponse(BaseModel):
    success: bool
    message: str
    cooldown_remaining_minutes: float = 0.0
    found_item_id: Optional[str] = None
    found_qty: int = 0

# ── Alchemy ──────────────────────────────────────────────────────────

class RefineRequest(BaseModel):
    recipe_id: str
    furnace_item_id: str = "furnace_mortal_iron"
    flame_item_id: str = "flame_wood"

class RefineResponse(BaseModel):
    success: bool
    message: str
    grade: Optional[str] = None
    impurity: Optional[float] = None
    heavenly_coincidence: bool = False
    alchemy_exp_gained: int = 0
    mastery: Dict[str, Any] = {}

class RecipeInfo(BaseModel):
    id: str
    name: str
    tier: int
    min_realm: int
    alchemy_level_req: int
    base_impurity: float
    materials: Dict[str, int]
    effects: Dict[str, Any]
    base_price: int
    blurb: str
    craftable_now: bool = False

class RecipesResponse(BaseModel):
    discord_id: str
    alchemy_level: int
    alchemy_title: str
    recipes: List[RecipeInfo]

# ── Forging ──────────────────────────────────────────────────────────

class CraftRequest(BaseModel):
    artifact_id: str

class CraftResponse(BaseModel):
    success: bool
    message: str
    chance: float = 0.0
    roll: float = 0.0
    forging_exp_gained: int = 0
    lost_materials: Dict[str, int] = {}
    mastery: Dict[str, Any] = {}

class EquipRequest(BaseModel):
    slot: str                  # weapon / armor / talisman / banner
    item_id: Optional[str] = None  # NULL/omitted = unequip

class EquipResponse(BaseModel):
    success: bool
    message: str
    equipped: Dict[str, Optional[str]]

# ── Economy ──────────────────────────────────────────────────────────

class MerchantStall(BaseModel):
    item_id: str
    name: str
    price_low_stones: int

class MerchantResponse(BaseModel):
    date_utc: str
    stalls: List[MerchantStall]
    message: str

class BuyRequest(BaseModel):
    item_id: str

class TradeResponse(BaseModel):
    success: bool
    message: str
    spirit_stones: int = 0

class SellRequest(BaseModel):
    item_id: str
    quality: Optional[str] = None
    quantity: int = Field(default=1, ge=1)

class ConvertRequest(BaseModel):
    direction: str             # "up" (wallet→grades) or "down" (grade→wallet)
    grade: str                 # mid / high / top
    amount: int = Field(ge=1)  # units of the relevant grade
