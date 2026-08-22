from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.balance import ALCHEMY, get_item
from models.user import User
from schemas.inventory import (
    BagResponse, BagEntry, ConsumeRequest, ConsumeResponse
)
from services.inventory_service import (
    list_bag, find_pill_stack, remove_item
)
from services.alchemy_engine import apply_recipe_effects, consumption_toxicity, grade_potency
from api.routes_cultivator import _get_user_or_404

router = APIRouter()


@router.get("/bag/{discord_id}", response_model=BagResponse)
async def get_bag(discord_id: str, db: AsyncSession = Depends(get_db)):
    """Returns the cultivator's spatial pouch (Qiankun Dai) and toxicity state."""
    user = await _get_user_or_404(discord_id, db)
    entries = await list_bag(db, user)

    bag_entries = []
    for e in entries:
        item_def = get_item(e.item_id) or {}
        bag_entries.append(BagEntry(
            item_id=e.item_id,
            name=item_def.get("name", e.item_id),
            category=item_def.get("category", "Unknown"),
            quality=e.quality,
            quantity=e.quantity,
            base_price=item_def.get("base_price", 0)
        ))
    bag_entries.sort(key=lambda b: (b.category, b.item_id, b.quality or ""))

    tox = user.pill_toxicity
    if tox >= 70:
        tox_msg = "🤢 Your meridians are SLUDGED with pill toxins — cultivation is heavily stifled! Cleanse yourself!"
    elif tox >= 35:
        tox_msg = "⚠️ Pill toxicity builds in your veins. Meditation slows; breakthroughs grow dangerous."
    else:
        tox_msg = "Your meridians run clean."

    return BagResponse(
        discord_id=user.discord_id,
        spirit_stones=user.spirit_stones,
        pill_toxicity=round(tox, 2),
        entries=bag_entries,
        message=tox_msg
    )


@router.post("/consume/{discord_id}", response_model=ConsumeResponse)
async def consume_item(discord_id: str, payload: ConsumeRequest, db: AsyncSession = Depends(get_db)):
    """
    Consumes a pill from the bag, applying grade-scaled effects.
    Impure pills add Pill Toxicity (*Dan Du*) — Flawless pills are toxin-free.
    """
    user = await _get_user_or_404(discord_id, db)

    if user.is_dead or user.soul_state == "DEAD":
        raise HTTPException(status_code=400, detail="The dead cannot swallow pills. Reincarnate first.")
    remnant = (user.soul_state == "REMNANT_SOUL" or user.is_remnant_soul)

    entry = await find_pill_stack(db, user, payload.item_id, payload.quality)
    if not entry:
        raise HTTPException(status_code=404, detail="No such pill in your pouch.")

    item_def = get_item(payload.item_id)
    if not item_def or item_def.get("category") != "Pill":
        raise HTTPException(status_code=400, detail="That item cannot be consumed.")

    # Recipes hold the effects; the stack's grade decides potency & toxicity
    from core.balance import PILL_RECIPES
    recipe = PILL_RECIPES.get(payload.item_id)
    if not recipe:
        raise HTTPException(status_code=400, detail="Unknown pill recipe.")

    grade = entry.quality or "Low"

    if "vitality_restore" in recipe["effects"] and not remnant:
        raise HTTPException(
            status_code=400,
            detail="The Heaven-Defying Rebirth Pill only benefits bodiless Remnant Souls."
        )

    effects = apply_recipe_effects(recipe, grade)
    messages = []

    if "qi_amount" in effects:
        before = user.spirit_energy
        user.spirit_energy = min(user.max_energy, user.spirit_energy + effects["qi_amount"])
        messages.append(f"+{user.spirit_energy - before:.1f} Qi surges through your meridians!")
    if "toxicity_cleanse" in effects:
        removed = min(user.pill_toxicity, effects["toxicity_cleanse"])
        user.pill_toxicity = max(0.0, user.pill_toxicity - effects["toxicity_cleanse"])
        messages.append(f"Pill toxins scoured away: -{removed:.1f} toxicity.")
    if "dao_heart_restore" in effects:
        gained = min(100.0 - user.dao_heart_stability, effects["dao_heart_restore"])
        user.dao_heart_stability = min(100.0, user.dao_heart_stability + effects["dao_heart_restore"])
        messages.append(f"Your Dao Heart stills. (+{gained:.1f} stability)")
    if "breakthrough_bonus" in effects:
        new_bonus = min(ALCHEMY["max_stored_breakthrough_bonus"],
                        user.stored_breakthrough_bonus + effects["breakthrough_bonus"])
        user.stored_breakthrough_bonus = new_bonus
        messages.append(f"Heavenly insight coils within you, awaiting your next breakthrough attempt. (+{new_bonus:.0%} stored)")
    if "lifespan_years" in effects:
        user.lifespan_max_years += effects["lifespan_years"]
        messages.append(f"The hands of fate retreat! Lifespan extended by {effects['lifespan_years']:.0f} years.")
    if "vitality_restore" in effects and remnant:
        user.remnant_soul_vitality = min(100.0, user.remnant_soul_vitality + effects["vitality_restore"])
        messages.append("Your soul-fire ROARS back to brilliance!")

    # Toxicity from residual impurities — Flawless adds none
    tox_gained = consumption_toxicity(grade)
    user.pill_toxicity = float(min(ALCHEMY["pill_toxicity_cap"], user.pill_toxicity + tox_gained))
    if tox_gained > 0:
        messages.append(f"☠️ Residual impurities settle into your marrow (+{tox_gained:.1f} Pill Toxicity).")

    await remove_item(db, user, payload.item_id, 1, grade)
    await db.commit()
    await db.refresh(user)

    potency_note = f"[{grade} · {grade_potency(grade):.2f}x potency]"
    return ConsumeResponse(
        success=True,
        message=f"{item_def['name']} {potency_note}: " + " ".join(messages),
        effects_applied=effects,
        toxicity_gained=tox_gained,
        pill_toxicity=round(user.pill_toxicity, 2)
    )
