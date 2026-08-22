from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone

from core.database import get_db
from core.balance import DAO_HEART
from models.user import User
from schemas.cultivator import (
    PossessRequest,
    SoulStateResponse,
    ReincarnateResponse
)
from services.soul_engine import (
    sync_remnant_vitality,
    execute_possession,
    calculate_reincarnation_benefits,
    compute_karmic_legacy
)
from services.root_engine import roll_root, roll_physique
from services.event_service import log_event
from api.routes_cultivator import _build_profile_response

router = APIRouter()


async def _get_user_or_404(discord_id: str, db: AsyncSession) -> User:
    stmt = select(User).where(User.discord_id == discord_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Cultivator not found in celestial records.")
    return user


def _soul_state_response(user: User, hours_as_soul: float, message: str) -> SoulStateResponse:
    return SoulStateResponse(
        discord_id=user.discord_id,
        soul_state=user.soul_state,
        is_dead=user.is_dead,
        is_remnant_soul=user.is_remnant_soul,
        remnant_soul_vitality=round(user.remnant_soul_vitality, 2),
        hours_as_soul=round(hours_as_soul, 2),
        karmic_legacy_tokens=user.karmic_legacy_tokens,
        lineage_generation=user.lineage_generation,
        death_count=user.death_count,
        message=message
    )


async def _sync_soul_decay(user: User, db: AsyncSession) -> tuple:
    """
    Lazily applies Remnant Soul vitality decay.
    Returns (hours_elapsed, extinguished). On extinguishing, converts the
    soul to TRUE DEATH and awards Karmic Legacy.
    """
    if user.soul_state != "REMNANT_SOUL":
        return 0.0, False

    res = sync_remnant_vitality(user.remnant_soul_vitality, user.remnant_soul_since)
    user.remnant_soul_vitality = res["vitality"]

    if res["extinguished"]:
        legacy = compute_karmic_legacy(
            user.highest_realm_achieved,
            user.total_breakthrough_wins
        )
        user.soul_state = "DEAD"
        user.is_dead = True
        user.is_remnant_soul = False
        user.death_count += 1
        user.karmic_legacy_tokens += legacy
        await db.commit()
        await db.refresh(user)
        return res["hours_elapsed"], True

    await db.commit()
    return res["hours_elapsed"], False


@router.get("/state/{discord_id}", response_model=SoulStateResponse)
async def get_soul_state(discord_id: str, db: AsyncSession = Depends(get_db)):
    """
    Inspects the soul state. Applies lazy vitality decay for Remnant Souls —
    a soul that burns out mid-inspection dies on the spot.
    """
    user = await _get_user_or_404(discord_id, db)
    hours, extinguished = await _sync_soul_decay(user, db)

    if extinguished:
        message = (
            "🕯️ You lingered too long between worlds... your soul-fire has EXTINGUISHED. "
            "True Death claims you — but your Karmic Legacy endures. Reincarnate when ready."
        )
    elif user.soul_state == "REMNANT_SOUL":
        message = (
            f"👻 You drift as a bodiless REMNANT SOUL. Vitality: {user.remnant_soul_vitality:.1f}/100 "
            f"({hours:.1f}h elapsed). Possess a vessel or reincarnate before the flame dies."
        )
    elif user.soul_state == "DEAD":
        message = (
            f"☠️ This cultivator is truly dead ({user.death_count} deaths recorded). "
            f"{user.karmic_legacy_tokens} Karmic Legacy tokens await the next incarnation."
        )
    else:
        message = "Your soul rests safely within its flesh. Live while you can."

    return _soul_state_response(user, hours, message)


@router.post("/possess/{discord_id}", response_model=SoulStateResponse)
async def attempt_possession(
    discord_id: str,
    payload: PossessRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Duo She — forcibly seize a mortal vessel. Success grants a fragile new body;
    failure burns precious soul vitality. Heaven marks this act as sin.
    """
    user = await _get_user_or_404(discord_id, db)

    if user.soul_state == "DEAD":
        raise HTTPException(status_code=400, detail="A dead soul cannot possess. Reincarnate via /api/soul/reincarnate.")
    if user.soul_state != "REMNANT_SOUL":
        raise HTTPException(status_code=400, detail="You already possess a living body.")

    hours, extinguished = await _sync_soul_decay(user, db)
    if extinguished:
        return _soul_state_response(
            user, hours,
            "🕯️ Your soul-fire extinguished before the ritual began. Reincarnate via /api/soul/reincarnate."
        )

    result = execute_possession(user.remnant_soul_vitality, payload.target_strength)
    user.karma_sin = min(DAO_HEART["karma_sin_max"], user.karma_sin + result["karma_gain"])

    if result["success"]:
        # A stolen body: alive again, but mortal and weakened
        user.soul_state = "ALIVE"
        user.is_remnant_soul = False
        user.is_dead = False
        user.remnant_soul_vitality = 100.0
        user.remnant_soul_since = None
        user.realm = 1
        user.stage = "Layer 1"
        user.spirit_energy = 20.0
        user.max_energy = 100.0
        user.qi_purity = 0.70
        user.meridian_damage = 0.0
        user.lifespan_current_years = 16.0
        user.lifespan_max_years = 120.0
        user.bottleneck_comprehension = user.bottleneck_comprehension * 0.5
        message = result["message"] + f" The body of {payload.target_name} is now yours... and your cultivation begins ANEW from Qi Condensation."
    else:
        user.remnant_soul_vitality = result["new_vitality"]
        if result.get("extinguished"):
            legacy = compute_karmic_legacy(user.highest_realm_achieved, user.total_breakthrough_wins)
            user.soul_state = "DEAD"
            user.is_dead = True
            user.is_remnant_soul = False
            user.death_count += 1
            user.karmic_legacy_tokens += legacy
            message = result["message"] + f" Your soul-form scatters... TRUE DEATH. {legacy} Karmic Legacy tokens pass on."
        else:
            message = result["message"] + f" Vitality: {user.remnant_soul_vitality:.1f}/100 remaining."

    if result["success"]:
        await log_event(db, user.discord_id, user.username, "possession",
                        {"target_name": payload.target_name})
    await db.commit()
    await db.refresh(user)
    return _soul_state_response(user, hours, message)


@router.post("/reincarnate/{discord_id}", response_model=ReincarnateResponse)
async def reincarnate(discord_id: str, db: AsyncSession = Depends(get_db)):
    """
    Voluntary or forced rebirth. Spends all Karmic Legacy tokens to bend fate:
    rare-root luck, starting wealth, and past-life insight retention.
    Begins Lineage Generation N+1.
    """
    user = await _get_user_or_404(discord_id, db)

    if user.soul_state == "ALIVE" and not user.is_dead:
        raise HTTPException(status_code=400, detail="You are still alive. Only the dead or bodiless may reincarnate.")

    # Remnant souls decaying into death still earn their legacy first
    await _sync_soul_decay(user, db)

    benefits = calculate_reincarnation_benefits(user.karmic_legacy_tokens)
    old_comprehension = user.bottleneck_comprehension

    chosen_root, purity = roll_root(luck_bonus=benefits["root_luck_bonus"])
    physique_name, physique_tier = roll_physique()

    # Fresh incarnation — new body, same eternal story
    user.username = user.username  # identity persists across generations
    user.dao_title = "Wandering Cultivator"
    user.realm = 1
    user.stage = "Layer 1"
    user.spirit_energy = 20.0
    user.max_energy = 100.0
    user.qi_purity = 0.70
    user.meridian_damage = 0.0
    user.lifespan_current_years = 16.0
    user.lifespan_max_years = 120.0
    user.is_bottleneck = False
    user.bottleneck_comprehension = round(old_comprehension * benefits["comprehension_retention_pct"], 2)
    user.dao_heart_stability = 100.0
    user.karma_sin = 0  # rebirth cleanses worldly sin
    user.spiritual_root = chosen_root
    user.spiritual_root_purity = purity
    user.physique_tier = physique_tier
    user.physique_name = physique_name
    user.soul_state = "ALIVE"
    user.is_dead = False
    user.is_remnant_soul = False
    user.remnant_soul_vitality = 100.0
    user.remnant_soul_since = None
    user.highest_realm_achieved = 1
    user.lineage_generation += 1
    user.spirit_stones = 15 + benefits["starting_stone_bonus"]
    user.karmic_legacy_tokens = 0  # spent on this life
    user.last_meditated = datetime.now(timezone.utc)
    user.last_action_date = None

    await db.commit()
    await db.refresh(user)

    await log_event(db, user.discord_id, user.username, "reincarnation", {
        "lineage_generation": user.lineage_generation,
        "spiritual_root": chosen_root,
        "physique_name": physique_name,
    })
    await db.commit()

    final_message = (
        f"{benefits['message']} You awaken as {user.username}, Generation {user.lineage_generation}, "
        f"born with {chosen_root} root and {physique_name}. The climb begins again — but wiser."
    ) if benefits["tokens_spent"] > 0 else (
        f"{benefits['message']} You awaken as {user.username}, Generation {user.lineage_generation}, "
        f"with {chosen_root} root and {physique_name}. The climb begins again."
    )

    return ReincarnateResponse(
        message=final_message,
        tokens_spent=benefits["tokens_spent"],
        root_luck_bonus=benefits["root_luck_bonus"],
        starting_stone_bonus=benefits["starting_stone_bonus"],
        lineage_generation=user.lineage_generation,
        profile=_build_profile_response(user)
    )
