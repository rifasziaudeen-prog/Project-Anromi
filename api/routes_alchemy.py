from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.balance import PILL_RECIPES, FURNACES, FLAMES
from models.user import User
from schemas.inventory import (
    RefineRequest, RefineResponse, RecipesResponse, RecipeInfo
)
from services.alchemy_engine import (
    compute_impurity,
    refine_outcome_message,
    xp_gain as pill_xp,
    level_from_exp,
)
from services.inventory_service import (
    consume_materials, has_materials, add_item, count_item
)
from api.routes_cultivator import _get_user_or_404

router = APIRouter()


@router.get("/recipes/{discord_id}", response_model=RecipesResponse)
async def get_recipes(discord_id: str, db: AsyncSession = Depends(get_db)):
    """Lists every known recipe with craftability for this cultivator."""
    user = await _get_user_or_404(discord_id, db)
    infos = []
    for rid, r in PILL_RECIPES.items():
        can = (
            user.realm >= r["min_realm"]
            and user.alchemy_level >= r["alchemy_level_req"]
            and await has_materials(db, user, r["materials"])
        )
        infos.append(RecipeInfo(
            id=rid, name=r["name"], tier=r["tier"],
            min_realm=r["min_realm"], alchemy_level_req=r["alchemy_level_req"],
            base_impurity=r["base_impurity"], materials=r["materials"],
            effects=r["effects"], base_price=r["base_price"], blurb=r["blurb"],
            craftable_now=can
        ))
    infos.sort(key=lambda i: (i.tier, i.id))
    mastery = level_from_exp(user.alchemy_exp)
    return RecipesResponse(
        discord_id=user.discord_id,
        alchemy_level=user.alchemy_level,
        alchemy_title=mastery["title"],
        recipes=infos
    )


@router.post("/refine/{discord_id}", response_model=RefineResponse)
async def refine_pill(discord_id: str, payload: RefineRequest, db: AsyncSession = Depends(get_db)):
    """
    Brews a pill. Quality is EARNED: impurities depend on your Alchemy Mastery
    (lower center + tighter spread) and equipment; Luck only fires rare
    'heavenly coincidences' toward purity.
    """
    user = await _get_user_or_404(discord_id, db)

    if user.is_dead or user.soul_state != "ALIVE":
        raise HTTPException(status_code=400, detail="Only the living may tend a furnace.")

    recipe = PILL_RECIPES.get(payload.recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Unknown pill recipe.")
    if user.realm < recipe["min_realm"]:
        raise HTTPException(
            status_code=400,
            detail=f"Your cultivation is too shallow for this Tier-{recipe['tier']} pill (requires Realm {recipe['min_realm']})."
        )
    if user.alchemy_level < recipe["alchemy_level_req"]:
        raise HTTPException(
            status_code=400,
            detail=f"Alchemy Mastery {recipe['alchemy_level_req']} required to attempt this pill."
        )

    furnace_def = FURNACES.get(payload.furnace_item_id)
    flame_def = FLAMES.get(payload.flame_item_id)
    if not furnace_def or not flame_def:
        raise HTTPException(status_code=404, detail="Unknown furnace or flame.")
    if await count_item(db, user, payload.furnace_item_id) < 1:
        raise HTTPException(status_code=400, detail=f"You do not own a {furnace_def['name']}.")
    if await count_item(db, user, payload.flame_item_id) < 1:
        raise HTTPException(status_code=400, detail=f"You need a {flame_def['name']} to fuel the furnace.")

    # Commit resources first — alchemy consumes its inputs win or lose
    ok = await consume_materials(db, user, recipe["materials"])
    if not ok:
        raise HTTPException(status_code=400, detail="Missing materials for this recipe.")
    from services.inventory_service import remove_item
    await remove_item(db, user, payload.flame_item_id, 1)

    roll = compute_impurity(
        recipe=recipe,
        furnace_impurity_reduction=furnace_def["impurity_reduction"],
        flame_impurity_reduction=flame_def["impurity_reduction"],
        alchemy_level=user.alchemy_level,
        luck_stat=user.luck_stat,
    )
    grade = roll["grade"]

    await add_item(db, user, payload.recipe_id, 1, quality=grade)

    gained_xp = pill_xp(recipe, grade)
    user.alchemy_exp += gained_xp
    old_level = user.alchemy_level
    mastery = level_from_exp(user.alchemy_exp)
    user.alchemy_level = mastery["level"]
    leveled_up = user.alchemy_level > old_level

    message = refine_outcome_message(grade, roll["heavenly_coincidence"], recipe["name"])
    if leveled_up:
        message += f" 🏆 ALCHEMY MASTERY RISES! You are now a {mastery['title']} (Level {mastery['level']})!"

    await db.commit()
    await db.refresh(user)

    return RefineResponse(
        success=True,
        message=message,
        grade=grade,
        impurity=roll["impurity"],
        heavenly_coincidence=roll["heavenly_coincidence"],
        alchemy_exp_gained=gained_xp,
        mastery=mastery
    )
