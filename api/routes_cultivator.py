from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
import random

from core.database import get_db
from core.balance import DAO_HEART, ALCHEMY, LUCK, TRIBULATION, get_physique_config, ARTIFACTS
from models.user import User
from models.realm import get_realm_meta, get_stages_for_realm, is_bottleneck_stage
from schemas.cultivator import (
    CultivatorRegister,
    CultivatorProfileResponse,
    MeditateResponse,
    BreakthroughOddsResponse,
    BreakthroughRequest,
    BreakthroughResultResponse,
    DaoHeartResponse
)
from services.cultivation_engine import (
    calculate_passive_energy_recovery,
    calculate_breakthrough_odds,
    execute_breakthrough,
    check_cultivation_deviation
)
from services.root_engine import roll_root, roll_physique
from services.alchemy_engine import mastery_title
from services.forging_engine import mastery_title as forging_mastery_title
from services.engagement_engine import (
    update_streak,
    today_str,
    maybe_windfall,
    maybe_promote_title
)
from services.soul_engine import resolve_death
from services.tribulation_engine import build_tribulation, serialize_state
from services.event_service import log_event

router = APIRouter()


EQUIP_SLOT_COLUMNS = ["equipped_weapon", "equipped_armor", "equipped_talisman", "equipped_banner"]


def _equipment_qi_bonus(user: User) -> float:
    """Sum of passive Qi bonuses from all equipped artifacts."""
    total = 0.0
    for col in EQUIP_SLOT_COLUMNS:
        item_id = getattr(user, col)
        if item_id and item_id in ARTIFACTS:
            total += ARTIFACTS[item_id]["passive_qi_bonus"]
    return round(total, 4)


def _build_profile_response(user: User) -> CultivatorProfileResponse:
    meta = get_realm_meta(user.realm)
    is_bottleneck = is_bottleneck_stage(user.realm, user.stage)
    return CultivatorProfileResponse(
        id=user.id,
        discord_id=user.discord_id,
        username=user.username,
        dao_title=user.dao_title,
        realm=user.realm,
        realm_name_en=meta["name_en"],
        realm_name_cn=meta["name_cn"],
        stage=user.stage,
        is_bottleneck=is_bottleneck,
        spirit_energy=round(user.spirit_energy, 2),
        max_energy=round(user.max_energy, 2),
        qi_purity=round(user.qi_purity, 2),
        meridian_damage=round(user.meridian_damage, 2),
        lifespan_current_years=round(user.lifespan_current_years, 2),
        lifespan_max_years=round(user.lifespan_max_years, 2),
        dao_heart_stability=round(user.dao_heart_stability, 2),
        karma_sin=user.karma_sin,
        spiritual_root=user.spiritual_root,
        spiritual_root_purity=user.spiritual_root_purity,
        physique_tier=user.physique_tier,
        physique_name=user.physique_name,
        is_dead=user.is_dead,
        is_remnant_soul=user.is_remnant_soul,
        soul_state=user.soul_state,
        remnant_soul_vitality=round(user.remnant_soul_vitality, 2),
        lineage_generation=user.lineage_generation,
        death_count=user.death_count,
        karmic_legacy_tokens=user.karmic_legacy_tokens,
        streak_days=user.streak_days,
        best_streak=user.best_streak,
        dao_insight=user.dao_insight,
        highest_realm_achieved=user.highest_realm_achieved,
        total_meditations=user.total_meditations,
        total_breakthrough_wins=user.total_breakthrough_wins,
        total_breakthrough_fails=user.total_breakthrough_fails,
        spirit_stones=user.spirit_stones,
        luck_stat=user.luck_stat,
        pill_toxicity=round(user.pill_toxicity, 2),
        stored_breakthrough_bonus=round(user.stored_breakthrough_bonus, 4),
        alchemy_level=user.alchemy_level,
        alchemy_title=mastery_title(user.alchemy_level),
        forging_level=user.forging_level,
        forging_title=forging_mastery_title(user.forging_level),
        last_meditated=user.last_meditated,
        created_at=user.created_at
    )


async def _get_user_or_404(discord_id: str, db: AsyncSession) -> User:
    stmt = select(User).where(User.discord_id == discord_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Cultivator not found in celestial records.")
    return user


async def _sync_passive_qi(user: User) -> None:
    """Lazily applies passive Qi recovery since the last action."""
    physique_cfg = get_physique_config(user.physique_name)
    new_energy, _ = calculate_passive_energy_recovery(
        current_energy=user.spirit_energy,
        max_energy=user.max_energy,
        last_meditated=user.last_meditated,
        realm=user.realm,
        stage=user.stage,
        root=user.spiritual_root,
        root_purity=user.spiritual_root_purity,
        meridian_damage=user.meridian_damage,
        physique_absorption_bonus=physique_cfg["qi_absorption_bonus"],
        equipment_qi_bonus=_equipment_qi_bonus(user),
        pill_toxicity=user.pill_toxicity
    )
    user.spirit_energy = new_energy
    user.last_meditated = datetime.now(timezone.utc)


@router.post("/register", response_model=CultivatorProfileResponse)
async def register_or_get_cultivator(
    payload: CultivatorRegister,
    db: AsyncSession = Depends(get_db)
):
    """
    Registers a new cultivator or fetches an existing profile.
    Rolls spiritual root (celestial gacha) and body constitution.
    """
    stmt = select(User).where(User.discord_id == payload.discord_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        chosen_root, purity = roll_root()
        physique_name, physique_tier = roll_physique()

        user = User(
            discord_id=payload.discord_id,
            username=payload.username,
            dao_title=payload.dao_title or "Wandering Cultivator",
            realm=1, # Qi Condensation
            stage="Layer 1",
            spirit_energy=20.0,
            max_energy=100.0,
            qi_purity=0.70,
            meridian_damage=0.0,
            lifespan_current_years=16.0,
            lifespan_max_years=120.0,
            dao_heart_stability=100.0,
            karma_sin=0,
            spiritual_root=chosen_root,
            spiritual_root_purity=purity,
            physique_tier=physique_tier,
            physique_name=physique_name,
            soul_state="ALIVE",
            streak_days=0,
            best_streak=0,
            last_action_date=today_str(),
            highest_realm_achieved=1,
            lineage_generation=1,
            luck_stat=LUCK["starting_luck"],
            spirit_stones=15
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return _build_profile_response(user)


@router.get("/profile/{discord_id}", response_model=CultivatorProfileResponse)
async def get_cultivator_profile(discord_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns full cultivation status, 16-realm state, longevity, Qi stats,
    soul state, and engagement progress.
    """
    user = await _get_user_or_404(discord_id, db)
    return _build_profile_response(user)


@router.post("/meditate/{discord_id}", response_model=MeditateResponse)
async def meditate(
    discord_id: str,
    ambient_spirit_density: float = Query(1.0, ge=0.1, le=10.0, description="Spirit density multiplier"),
    db: AsyncSession = Depends(get_db)
):
    """
    Deep closed-door meditation: absorbs ambient Qi (streak-multiplied),
    risks Qi Deviation at low Dao Heart, and may trigger random epiphany windfalls.
    """
    user = await _get_user_or_404(discord_id, db)

    if user.is_dead or user.soul_state == "DEAD":
        raise HTTPException(status_code=400, detail="The cultivator has perished. Reincarnate via /api/soul/reincarnate.")
    if user.is_remnant_soul or user.soul_state == "REMNANT_SOUL":
        raise HTTPException(status_code=400, detail="A bodiless soul cannot meditate. Possess a vessel or reincarnate via /api/soul.")
    if user.active_tribulation:
        raise HTTPException(status_code=400, detail="Heaven's lightning owns this moment. Face your tribulation via /api/tribulation/action.")

    physique_cfg = get_physique_config(user.physique_name)
    new_energy, gathered = calculate_passive_energy_recovery(
        current_energy=user.spirit_energy,
        max_energy=user.max_energy,
        last_meditated=user.last_meditated,
        realm=user.realm,
        stage=user.stage,
        root=user.spiritual_root,
        root_purity=user.spiritual_root_purity,
        meridian_damage=user.meridian_damage,
        ambient_spirit_density=ambient_spirit_density,
        physique_absorption_bonus=physique_cfg["qi_absorption_bonus"],
        equipment_qi_bonus=_equipment_qi_bonus(user),
        pill_toxicity=user.pill_toxicity
    )

    # Daily streak resolution (habit loop)
    streak_res = update_streak(user.last_action_date, user.streak_days)
    user.streak_days = streak_res["streak_days"]
    user.best_streak = max(user.best_streak, user.streak_days)
    user.last_action_date = today_str()
    user.total_meditations += 1

    # Streak multiplier rewards consistency (extra Qi on top of base absorption)
    streak_mult = streak_res["multiplier"]
    if gathered > 0 and streak_mult > 1.0:
        headroom = max(0.0, user.max_energy - new_energy)
        user.spirit_energy = min(user.max_energy, new_energy + min(headroom, gathered * (streak_mult - 1.0)))
    else:
        user.spirit_energy = new_energy
    gathered *= streak_mult

    message_parts = []
    if gathered > 0:
        message_parts.append(f"Meditated peacefully and gathered {gathered:.1f} spiritual Qi.")
    else:
        message_parts.append("Meridians are full of spiritual energy. Ready to attempt breakthrough!")
    if streak_res["changed"]:
        message_parts.append(streak_res["message"])

    # Qi Deviation risk when Dao Heart is shattered
    deviation_triggered = False
    episode = check_cultivation_deviation(user.dao_heart_stability)
    if episode:
        deviation_triggered = True
        user.spirit_energy = max(0.0, user.spirit_energy * (1.0 - episode["qi_loss_ratio"]))
        user.dao_heart_stability = max(0.0, user.dao_heart_stability - episode["dao_heart_loss"])
        user.karma_sin = min(DAO_HEART["karma_sin_max"], user.karma_sin + episode["karma_gain"])
        message_parts.append(episode["message"])

    # Variable-ratio windfall (jackpot moment) — Luck bends the odds
    windfall = maybe_windfall(luck_stat=user.luck_stat)
    dao_insight_gained = 0
    if windfall:
        dao_insight_gained = windfall["insight"]
        user.dao_insight += windfall["insight"]
        user.bottleneck_comprehension = min(10.0, user.bottleneck_comprehension + windfall["insight"])
        if windfall["spirit_stones"]:
            user.spirit_stones += windfall["spirit_stones"]
        message_parts.append(windfall["message"])
        await log_event(db, user.discord_id, user.username, "windfall",
                        {"windfall_message": windfall["message"]})

    # Slight natural healing of meridians during meditation
    if user.meridian_damage > 0.0:
        user.meridian_damage = max(0.0, user.meridian_damage - 0.01)

    # Slow natural cleanse of pill toxins through steady cultivation
    if user.pill_toxicity > 0.0:
        user.pill_toxicity = max(0.0, user.pill_toxicity - ALCHEMY["natural_decay_per_meditation"])

    await db.commit()
    await db.refresh(user)

    is_full = user.spirit_energy >= user.max_energy
    can_breakthrough = user.spirit_energy >= (user.max_energy * 0.85)

    return MeditateResponse(
        message=" ".join(message_parts),
        qi_gathered=round(gathered, 2),
        spirit_energy=round(user.spirit_energy, 2),
        max_energy=round(user.max_energy, 2),
        is_full=is_full,
        can_breakthrough=can_breakthrough,
        meridian_damage=round(user.meridian_damage, 2),
        streak_days=user.streak_days,
        streak_multiplier=streak_res["multiplier"],
        dao_insight_gained=dao_insight_gained,
        deviation_triggered=deviation_triggered,
        windfall=windfall
    )


@router.get("/breakthrough-odds/{discord_id}", response_model=BreakthroughOddsResponse)
async def get_breakthrough_odds(
    discord_id: str,
    pill_bonus: float = Query(0.0, ge=0.0, le=1.0),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculates detailed odds for breaking through to the next layer, sub-stage, or major realm.
    """
    user = await _get_user_or_404(discord_id, db)

    await _sync_passive_qi(user)
    await db.commit()

    odds = calculate_breakthrough_odds(
        realm=user.realm,
        stage=user.stage,
        current_energy=user.spirit_energy,
        max_energy=user.max_energy,
        qi_purity=user.qi_purity,
        dao_heart=user.dao_heart_stability,
        meridian_damage=user.meridian_damage,
        bottleneck_insight=user.bottleneck_comprehension,
        pill_bonus=pill_bonus
    )

    return BreakthroughOddsResponse(
        can_attempt=odds["can_attempt"],
        is_bottleneck=odds.get("is_bottleneck", False),
        is_realm_leap=odds.get("is_realm_leap", False),
        base_chance=odds.get("base_chance", 0.0),
        modifiers=odds.get("modifiers", {}),
        final_chance=odds.get("final_chance", 0.0),
        target_realm=odds.get("target_realm", user.realm),
        target_stage=odds.get("target_stage", user.stage),
        reason=odds.get("reason")
    )


@router.post("/breakthrough/{discord_id}", response_model=BreakthroughResultResponse)
async def attempt_cultivator_breakthrough(
    discord_id: str,
    payload: BreakthroughRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Executes a breakthrough attempt. Advances layers/realms on success;
    backlash, Qi Deviation-grade trauma, and even PERMADEATH on failure.
    """
    user = await _get_user_or_404(discord_id, db)

    if user.is_dead or user.soul_state == "DEAD":
        raise HTTPException(status_code=400, detail="The cultivator has perished. Reincarnate via /api/soul/reincarnate.")
    if user.is_remnant_soul or user.soul_state == "REMNANT_SOUL":
        raise HTTPException(status_code=400, detail="A bodiless soul cannot force a breakthrough.")
    if user.active_tribulation:
        raise HTTPException(status_code=400, detail="A Heavenly Tribulation rages! Face it via /api/tribulation/action.")

    await _sync_passive_qi(user)

    physique_cfg = get_physique_config(user.physique_name)
    res = execute_breakthrough(
        realm=user.realm,
        stage=user.stage,
        current_energy=user.spirit_energy,
        max_energy=user.max_energy,
        qi_purity=user.qi_purity,
        dao_heart=user.dao_heart_stability,
        meridian_damage=user.meridian_damage,
        bottleneck_insight=user.bottleneck_comprehension,
        pill_bonus=(payload.pill_bonus or 0.0) + user.stored_breakthrough_bonus,
        physique_guard=physique_cfg["dao_heart_guard"],
        pill_toxicity=user.pill_toxicity
    )
    # Booster pills are spent on the attempt, success or failure
    user.stored_breakthrough_bonus = 0.0

    soul_fate = None
    legacy_awarded = 0
    title_promoted = False

    if res["outcome"] != "INSUFFICIENT_QI":
        old_realm = user.realm

        # ── HEAVEN BARS THE WAY ──
        # A successful major leap into Realm 4+ summons a Tribulation instead
        # of instant advancement. Survive the storm to claim the new realm.
        if res["success"] and res["realm"] > old_realm and res["realm"] >= TRIBULATION["min_target_realm"]:
            equipped_defs = {}
            for slot, col in (("weapon", "equipped_weapon"), ("armor", "equipped_armor"), ("banner", "equipped_banner")):
                item_id = getattr(user, col)
                equipped_defs[slot] = ARTIFACTS.get(item_id) if item_id else None
            physique_cfg = get_physique_config(user.physique_name)
            stages_now = get_stages_for_realm(user.realm)
            stage_index = stages_now.index(user.stage) if user.stage in stages_now else 0

            state = build_tribulation(
                target_realm=res["realm"],
                spiritual_root=user.spiritual_root,
                karma_sin=user.karma_sin,
                spirit_energy=user.spirit_energy,
                max_energy=user.max_energy,
                physique_tier=physique_cfg["tier"],
                physique_resistance=physique_cfg["tribulation_resistance"],
                luck_stat=user.luck_stat,
                dao_heart=user.dao_heart_stability,
                equipped=equipped_defs,
                stage_index=stage_index
            )
            user.active_tribulation = serialize_state(state)
            await log_event(db, user.discord_id, user.username, "tribulation_summoned", {
                "target_realm": res["realm"], "tier": state["tier"],
                "total_strikes": state["total_strikes"]
            })
            await db.commit()
            await db.refresh(user)

            target_meta = get_realm_meta(res["realm"])
            current_meta = get_realm_meta(user.realm)
            return BreakthroughResultResponse(
                success=True,
                outcome="TRIBULATION_REQUIRED",
                message=(
                    f"⚡ Your Qi SHATTERS the barrier — and Heaven Answers! A "
                    f"{state['tier'].replace('_', '-')} Tribulation of {state['total_strikes']} strikes "
                    f"descends upon your crossing into the {target_meta['name_en']} Realm! "
                    f"Face it: POST /api/tribulation/initiate, then /api/tribulation/action each wave."
                ),
                roll=res.get("roll"),
                needed=res.get("needed"),
                realm=user.realm,
                realm_name_en=current_meta["name_en"],
                realm_name_cn=current_meta["name_cn"],
                stage=user.stage,
                spirit_energy=round(user.spirit_energy, 2),
                max_energy=round(user.max_energy, 2),
                dao_heart=round(user.dao_heart_stability, 2),
                meridian_damage=round(user.meridian_damage, 2),
                is_dead=False,
                is_remnant_soul=False,
                near_miss=False,
                body_destroyed=False,
                soul_fate=None,
                karmic_legacy_awarded=0,
                title_promoted=False
            )

        user.realm = res["realm"]
        user.stage = res["stage"]
        user.spirit_energy = res["current_energy"]
        user.max_energy = res["max_energy"]
        user.dao_heart_stability = res["dao_heart"]
        user.meridian_damage = res["meridian_damage"]

        if res["success"]:
            user.total_breakthrough_wins += 1
            user.highest_realm_achieved = max(user.highest_realm_achieved, user.realm)
            if user.realm > old_realm:
                user.dao_title, title_promoted = maybe_promote_title(user.dao_title, user.realm)
        else:
            user.total_breakthrough_fails += 1
            if res.get("consolation_insight"):
                user.dao_insight += res["consolation_insight"]
                user.bottleneck_comprehension = min(10.0, user.bottleneck_comprehension + res["consolation_insight"])

        # Permadeath resolution — the single most emotionally charged moment
        if res.get("body_destroyed"):
            death = resolve_death(
                realm=res["realm"],
                highest_realm=user.highest_realm_achieved,
                total_breakthrough_wins=user.total_breakthrough_wins
            )
            soul_fate = death["fate"]
            legacy_awarded = death["legacy_awarded"]
            user.death_count += 1
            user.remnant_soul_vitality = death["vitality"]
            if death["survived_as_soul"]:
                user.soul_state = "REMNANT_SOUL"
                user.is_remnant_soul = True
                user.is_dead = False
                user.remnant_soul_since = datetime.now(timezone.utc)
                user.spirit_energy = 0.0
            else:
                user.soul_state = "DEAD"
                user.is_dead = True
                user.is_remnant_soul = False
                user.karmic_legacy_tokens += legacy_awarded
            res["message"] += " " + death["message"]

        # Recalculate lifespan max on realm upgrade
        meta = get_realm_meta(user.realm)
        if meta["base_lifespan_years"] > user.lifespan_max_years:
            user.lifespan_max_years = float(meta["base_lifespan_years"])

        # Chronicle: heaven's ledger records this moment
        if res["success"]:
            await log_event(db, user.discord_id, user.username, "breakthrough", {
                "realm": user.realm, "realm_name_en": meta["name_en"],
                "stage": user.stage, "dao_title": user.dao_title
            })
        elif soul_fate == "TRUE_DEATH":
            await log_event(db, user.discord_id, user.username, "true_death", {
                "realm": res["realm"], "legacy_awarded": legacy_awarded
            })

        await db.commit()
        await db.refresh(user)

    meta = get_realm_meta(user.realm)

    return BreakthroughResultResponse(
        success=res["success"],
        outcome=res["outcome"],
        message=res["message"],
        roll=res.get("roll"),
        needed=res.get("needed"),
        realm=user.realm,
        realm_name_en=meta["name_en"],
        realm_name_cn=meta["name_cn"],
        stage=user.stage,
        spirit_energy=round(user.spirit_energy, 2),
        max_energy=round(user.max_energy, 2),
        dao_heart=round(user.dao_heart_stability, 2),
        meridian_damage=round(user.meridian_damage, 2),
        is_dead=user.is_dead,
        is_remnant_soul=user.is_remnant_soul,
        near_miss=res.get("near_miss", False),
        body_destroyed=res.get("body_destroyed", False),
        soul_fate=soul_fate,
        karmic_legacy_awarded=legacy_awarded,
        title_promoted=title_promoted
    )


@router.get("/dao-heart/{discord_id}", response_model=DaoHeartResponse)
async def get_dao_heart(discord_id: str, db: AsyncSession = Depends(get_db)):
    """
    Inspects mental stability (Dao Xin), deviation risk, and demonic karma.
    """
    user = await _get_user_or_404(discord_id, db)

    dh = user.dao_heart_stability
    threshold = DAO_HEART["deviation_threshold"]
    if dh >= 80:
        status = "Serene"
    elif dh >= 50:
        status = "Turbulent"
    elif dh >= threshold:
        status = "Critical"
    else:
        status = "Deviation Risk"

    depth_ratio = max(0.0, (threshold - dh)) / max(1.0, threshold)
    risk = 0.0 if dh >= threshold else min(0.75, DAO_HEART["deviation_base_chance"] * (0.5 + depth_ratio))

    sin = user.karma_sin
    if sin < 100:
        karma_class = "Pure"
    elif sin < 300:
        karma_class = "Tainted"
    elif sin < 600:
        karma_class = "Demonic"
    else:
        karma_class = "Heaven's Enemy"

    if status == "Deviation Risk":
        message = (
            f"⚠️ WARNING: Dao Heart at {dh:.0f}/100! Inner demons circle your mind. "
            f"Meditating risks Qi Deviation ({risk:.0%} chance per session). Restore your will through breakthroughs."
        )
    elif sin >= 300:
        message = f"Your Dao Heart holds ({dh:.0f}/100), but Heaven's ledger darkens — {sin} Sin Karma accrued."
    else:
        message = f"Your Dao Heart stands firm at {dh:.0f}/100. The path ahead is clear."

    return DaoHeartResponse(
        discord_id=user.discord_id,
        dao_heart_stability=round(dh, 2),
        status=status,
        deviation_risk_chance=round(risk, 4),
        deviation_threshold=threshold,
        karma_sin=sin,
        karma_class=karma_class,
        message=message
    )
