from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from core.database import get_db
from core.balance import NARRATION
from models.realm import get_realm_meta
from schemas.cultivator import CultivatorProfileResponse
from services.narration_service import generate_narration, available_providers
from services.event_service import log_event, get_recent_events, event_to_dict
from api.routes_cultivator import _get_user_or_404, _build_profile_response

router = APIRouter()


class NarrateRequest(BaseModel):
    event_type: str
    extra: Optional[Dict[str, Any]] = None   # e.g. {"windfall_message": "...", "target_name": "..."}

class NarrateResponse(BaseModel):
    narration: str
    provider: Optional[str] = None
    model: Optional[str] = None
    fell_back: bool = False

class NarrationStatusResponse(BaseModel):
    persona: str
    configured_providers: List[str]
    message: str


def _build_context(user, extra: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    meta = get_realm_meta(user.realm)
    ctx = {
        "username": user.username,
        "dao_title": user.dao_title,
        "realm": user.realm,
        "realm_name_en": meta["name_en"],
        "realm_name_cn": meta["name_cn"],
        "stage": user.stage,
        "spiritual_root": user.spiritual_root,
        "physique_name": user.physique_name,
        "lineage_generation": user.lineage_generation,
        "karma_sin": user.karma_sin,
        "dao_heart": round(user.dao_heart_stability, 1),
    }
    if extra:
        ctx.update(extra)
    return ctx


@router.get("/status", response_model=NarrationStatusResponse)
async def narration_status():
    """Which LLM providers are configured for The Heavenly Dao right now."""
    providers = available_providers()
    return NarrationStatusResponse(
        persona=NARRATION["persona_name"],
        configured_providers=providers,
        message=(
            f"The Heavenly Dao speaks through: {', '.join(providers)}."
            if providers else
            "No LLM keys configured — The Heavenly Dao speaks in whispers (canned fallback lines). "
            "Add GROQ_API_KEY / GEMINI_API_KEY / OPENROUTER_API_KEY to .env."
        )
    )


@router.post("/narrate/{discord_id}", response_model=NarrateResponse)
async def narrate_event(discord_id: str, payload: NarrateRequest, db: AsyncSession = Depends(get_db)):
    """
    The Heavenly Dao narrates a moment from this cultivator's life.
    Event types: breakthrough, tribulation_summoned, tribulation_survived,
    tribulation_destroyed, true_death, windfall, reincarnation, possession.
    """
    user = await _get_user_or_404(discord_id, db)
    context = _build_context(user, payload.extra)
    result = await generate_narration(payload.event_type, context)
    return NarrateResponse(**result)


@router.get("/events/recent")
async def recent_events(
    since_id: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """
    Chronicle feed for the Discord announcer bot: poll with since_id
    to receive only new events, in order.
    """
    events = await get_recent_events(db, since_id=since_id, limit=limit)
    return {"events": [event_to_dict(e) for e in events], "last_id": events[-1].id if events else since_id}
