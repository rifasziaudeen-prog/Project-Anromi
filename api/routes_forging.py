from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.balance import ARTIFACTS, ARTIFACT_SLOTS
from models.user import User
from schemas.inventory import CraftRequest, CraftResponse, EquipRequest, EquipResponse
from services.forging_engine import attempt_forge, xp_to_level, mastery_title
from services.inventory_service import consume_materials, add_item, count_item
from api.routes_cultivator import _get_user_or_404

router = APIRouter()

SLOT_COLUMN = {"weapon": "equipped_weapon", "armor": "equipped_armor",
               "talisman": "equipped_talisman", "banner": "equipped_banner"}


@router.post("/craft/{discord_id}", response_model=CraftResponse)
async def craft_artifact(discord_id: str, payload: CraftRequest, db: AsyncSession = Depends(get_db)):
    """
    Forges an artifact. Failure devours half the materials — but every swing
    of the hammer teaches (XP even on failure).
    """
    user = await _get_user_or_404(discord_id, db)

    if user.is_dead or user.soul_state != "ALIVE":
        raise HTTPException(status_code=400, detail="Only the living may hammer spirit-metal.")

    artifact = ARTIFACTS.get(payload.artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Unknown artifact blueprint.")
    if user.forging_level < artifact["forging_level_req"]:
        raise HTTPException(
            status_code=400,
            detail=f"Forging Mastery {artifact['forging_level_req']} required for {artifact['tier'].title()}-tier work."
        )
    if not await has_enough_materials(db, user, artifact):
        from core.balance import ITEMS_REGISTRY
        missing = ", ".join(f"{ITEMS_REGISTRY[m]['name']} x{q}" for m, q in artifact["materials"].items())
        raise HTTPException(status_code=400, detail=f"Missing materials: {missing}.")

    # Consume everything up front; refund survivors on failure
    await consume_materials(db, user, artifact["materials"])

    result = attempt_forge(artifact, user.forging_level)

    if result["success"]:
        await add_item(db, user, artifact["id"], 1)
    else:
        from services.inventory_service import add_item as _add
        for mat_id, orig_qty in artifact["materials"].items():
            survivors = orig_qty - result["lost_materials"].get(mat_id, 0)
            if survivors > 0:
                await _add(db, user, mat_id, survivors)

    user.forging_exp += result["xp_gain"]
    old_level = user.forging_level
    mastery = xp_to_level(user.forging_exp)
    user.forging_level = mastery["level"]
    leveled_up = user.forging_level > old_level

    message = result["message"]
    if leveled_up:
        message += f" 🏆 FORGING MASTERY RISES! You are now a {mastery['title']} (Level {mastery['level']})!"

    await db.commit()
    await db.refresh(user)

    return CraftResponse(
        success=result["success"],
        message=message,
        chance=result["chance"],
        roll=result["roll"],
        forging_exp_gained=result["xp_gain"],
        lost_materials={} if result["success"] else result["lost_materials"],
        mastery=mastery
    )


async def has_enough_materials(db: AsyncSession, user: User, artifact) -> bool:
    for mat_id, qty in artifact["materials"].items():
        if await count_item(db, user, mat_id) < qty:
            return False
    return True


@router.post("/equip/{discord_id}", response_model=EquipResponse)
async def equip_artifact(discord_id: str, payload: EquipRequest, db: AsyncSession = Depends(get_db)):
    """Equips or unequips an owned artifact into its designated slot."""
    user = await _get_user_or_404(discord_id, db)

    if payload.slot not in SLOT_COLUMN:
        raise HTTPException(status_code=400, detail="Slot must be one of: weapon, armor, talisman, banner.")

    column = SLOT_COLUMN[payload.slot]
    if payload.item_id is None:
        setattr(user, column, None)
        await db.commit()
        await db.refresh(user)
        return EquipResponse(success=True, message="Slot emptied.",
                             equipped=_equipped_map(user))

    artifact = ARTIFACTS.get(payload.item_id)
    if not artifact or artifact["slot"] != payload.slot:
        raise HTTPException(status_code=400, detail="That artifact does not fit this slot.")
    if await count_item(db, user, payload.item_id) < 1:
        raise HTTPException(status_code=400, detail=f"You do not own the {artifact['name']}.")

    setattr(user, column, payload.item_id)
    await db.commit()
    await db.refresh(user)
    return EquipResponse(
        success=True,
        message=f"{artifact['name']} hums to life, bound to your aura. (+{artifact['passive_qi_bonus']:.0%} Qi absorption)",
        equipped=_equipped_map(user)
    )


def _equipped_map(user: User):
    return {
        "weapon": user.equipped_weapon,
        "armor": user.equipped_armor,
        "talisman": user.equipped_talisman,
        "banner": user.equipped_banner,
    }


@router.get("/blueprints")
async def list_blueprints():
    """All known artifact blueprints with requirements."""
    return [
        {
            "id": a["id"], "name": a["name"], "slot": a["slot"], "tier": a["tier"],
            "passive_qi_bonus": a["passive_qi_bonus"],
            "tribulation_resistance": a["tribulation_resistance"],
            "forging_level_req": a["forging_level_req"],
            "materials": a["materials"],
        }
        for a in ARTIFACTS.values()
    ]
