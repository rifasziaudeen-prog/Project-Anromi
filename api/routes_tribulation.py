from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from core.database import get_db
from core.balance import (
    TRIBULATION, SOUL, BREAKTHROUGH, ARTIFACTS, get_physique_config
)
from models.user import User
from models.realm import get_realm_meta, get_stages_for_realm
from schemas.world import (
    TribulationStateResponse, TribulationActionRequest,
    TribulationActionResponse, TribulationSummaryModel
)
from services.tribulation_engine import (
    deserialize_state, serialize_state, resolve_wave,
    tribulation_summary, near_miss_death
)
from services.soul_engine import resolve_death
from services.engagement_engine import maybe_promote_title
from services.inventory_service import remove_item, find_pill_stack
from services.event_service import log_event
from api.routes_cultivator import _get_user_or_404

router = APIRouter()

EQUIP_SLOT_COLUMNS = {"weapon": "equipped_weapon", "armor": "equipped_armor", "banner": "equipped_banner"}


def _summary_model(state) -> TribulationSummaryModel:
    return TribulationSummaryModel(**tribulation_summary(state))


@router.get("/state/{discord_id}", response_model=TribulationStateResponse)
async def get_tribulation_state(discord_id: str, db: AsyncSession = Depends(get_db)):
    """Inspects an ongoing tribulation, if any."""
    user = await _get_user_or_404(discord_id, db)
    state = deserialize_state(user.active_tribulation)
    if not state:
        return TribulationStateResponse(active=False, message="No storm gathers above you. Cultivate in peace.")
    return TribulationStateResponse(
        active=True,
        summary=_summary_model(state),
        log_tail=state.get("log", [])[-5:],
        message=f"A {state['tier'].replace('_', '-')} Tribulation rages — {state['total_strikes'] - state['strikes_done_total']} strikes remain."
    )


@router.post("/initiate/{discord_id}", response_model=TribulationStateResponse)
async def initiate(discord_id: str, db: AsyncSession = Depends(get_db)):
    """
    Steps into the storm. The tribulation was summoned by your breakthrough
    attempt — this endpoint confirms you are ready for Wave 1.
    """
    user = await _get_user_or_404(discord_id, db)
    state = deserialize_state(user.active_tribulation)
    if not state:
        raise HTTPException(status_code=400, detail="No tribulation awaits you. Attempt a major realm breakthrough first.")
    return TribulationStateResponse(
        active=True,
        summary=_summary_model(state),
        log_tail=state.get("log", [])[-3:],
        message="☁️ You step onto the peak. Choose your action for each wave wisely: endure, sacrifice a treasure, swallow a shield pill... or flee in shame."
    )


@router.post("/action/{discord_id}", response_model=TribulationActionResponse)
async def tribulation_action(discord_id: str, payload: TribulationActionRequest, db: AsyncSession = Depends(get_db)):
    """
    Resolves ONE WAVE of your tribulation.
    Actions: endure | sacrifice:<weapon|armor|banner> | pill | bail
    """
    user = await _get_user_or_404(discord_id, db)
    state = deserialize_state(user.active_tribulation)
    if not state:
        raise HTTPException(status_code=400, detail="No active tribulation.")

    action = payload.action.strip().lower()

    # Shield pill: swallowing it IS your action for this wave (you endure behind the ward)
    if action == "pill":
        entry = await find_pill_stack(db, user, "tribulation_shield_pill")
        if not entry:
            raise HTTPException(status_code=400, detail="You carry no Tribulation Shield Pills.")
        from core.balance import PILL_RECIPES
        from services.alchemy_engine import apply_recipe_effects
        effects = apply_recipe_effects(PILL_RECIPES["tribulation_shield_pill"], entry.quality or "Low")
        await remove_item(db, user, "tribulation_shield_pill", 1, entry.quality)
        state["shield"] += float(effects.get("tribulation_shield", 0))
        state["log"].append(f"🛡️ You crush a shield pill between your teeth. A ward of metal-Qi wraps you (+{effects.get('tribulation_shield', 0):.0f}).")
        action = "endure"

    result = resolve_wave(state, action)

    if result["outcome"] == "INVALID":
        await db.commit()
        return TribulationActionResponse(outcome="INVALID", events=result["events"])

    if result["outcome"] == "BAILED":
        user.active_tribulation = None
        user.meridian_damage = min(1.0, user.meridian_damage + TRIBULATION["bail_meridian_penalty"])
        user.dao_heart_stability = max(0.0, user.dao_heart_stability - TRIBULATION["bail_dao_heart_loss"])
        user.karma_sin = min(1000, user.karma_sin + TRIBULATION["bail_karma_gain"])
        await _sync_destroyed_gear(db, user, state)
        await db.commit()
        await db.refresh(user)
        return TribulationActionResponse(
            outcome="BAILED",
            events=result["events"] + [
                f"You survive, but heaven's ledger darkens: Meridian +{TRIBULATION['bail_meridian_penalty']:.0%}, "
                f"Dao Heart -{TRIBULATION['bail_dao_heart_loss']:.0f}, Karma +{TRIBULATION['bail_karma_gain']}."
            ],
            destroyed_artifacts=state.get("destroyed_artifacts", [])
        )

    if result["outcome"] == "ONGOING":
        user.active_tribulation = serialize_state(result["state"])
        await db.commit()
        await db.refresh(user)
        return TribulationActionResponse(
            outcome="ONGOING",
            events=result["events"],
            summary=_summary_model(result["state"]),
            destroyed_artifacts=result["state"].get("destroyed_artifacts", [])
        )

    # ── Storm finished one way or another ──
    final_state = result["state"]
    user.active_tribulation = None
    user.meridian_damage = min(1.0, max(user.meridian_damage, final_state.get("_meridian_damage", 0.0)))
    await _sync_destroyed_gear(db, user, final_state)

    if result["outcome"] == "SURVIVED":
        events = list(result["events"])
        target = final_state["target_realm"]
        meta = get_realm_meta(target)
        old_title = user.dao_title
        user.realm = target
        user.stage = meta["stages"][0]
        user.max_energy = meta["base_max_qi"]
        user.spirit_energy = meta["base_max_qi"] * BREAKTHROUGH["realm_leap_energy_pct"]
        if meta["base_lifespan_years"] > user.lifespan_max_years:
            user.lifespan_max_years = float(meta["base_lifespan_years"])
        user.dao_heart_stability = min(100.0, user.dao_heart_stability + TRIBULATION["survive_dao_heart_gain"])
        user.highest_realm_achieved = max(user.highest_realm_achieved, target)
        user.total_breakthrough_wins += 1
        promoted_title, _ = maybe_promote_title(old_title, target)
        if promoted_title != old_title:
            user.dao_title = promoted_title
            events.append(f"👑 The world will speak of you differently now: {promoted_title}.")
        events.append(f"⚡ You have stepped into the {meta['name_en']} Realm ({user.stage})!")
        await log_event(db, user.discord_id, user.username, "tribulation_survived", {
            "strikes_endured": final_state["strikes_done_total"],
            "realm_advanced_to": target,
        })
        await db.commit()
        await db.refresh(user)
        return TribulationActionResponse(
            outcome="SURVIVED",
            events=events,
            realm_advanced_to=target,
            summary=_summary_model(final_state),
            destroyed_artifacts=final_state.get("destroyed_artifacts", [])
        )

    # DESTROYED — permadeath hook: the crossing soul ALWAYS escapes as a Remnant Soul
    events = list(result["events"])
    death = resolve_death(
        realm=max(user.realm, SOUL["remnant_min_realm"]),
        highest_realm=user.highest_realm_achieved,
        total_breakthrough_wins=user.total_breakthrough_wins
    )
    user.soul_state = "REMNANT_SOUL"
    user.is_remnant_soul = True
    user.is_dead = False
    user.death_count += 1
    user.remnant_soul_vitality = death["vitality"]
    user.remnant_soul_since = datetime.now(timezone.utc)
    user.spirit_energy = 0.0
    events.append(death["message"])
    if near_miss_death(final_state):
        events.append("💔 SO CLOSE! One or two strikes from godhood... the heavens are cruel.")
    await log_event(db, user.discord_id, user.username, "tribulation_destroyed", {
        "strikes_endured": final_state["strikes_done_total"],
    })
    await db.commit()
    await db.refresh(user)
    return TribulationActionResponse(
        outcome="DESTROYED",
        events=events,
        soul_fate="REMNANT_SOUL",
        summary=_summary_model(final_state),
        destroyed_artifacts=final_state.get("destroyed_artifacts", [])
    )


async def _sync_destroyed_gear(db: AsyncSession, user: User, state) -> None:
    """Artifacts shattered mid-storm leave both your body AND your pouch."""
    destroyed_ids = set()
    for slot, col in EQUIP_SLOT_COLUMNS.items():
        g = state["gear"].get(slot)
        if g is None and getattr(user, col):
            destroyed_ids.add(getattr(user, col))
            setattr(user, col, None)
    for item_id in destroyed_ids:
        await remove_item(db, user, item_id, 1)
