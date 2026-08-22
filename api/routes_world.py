from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone

from core.database import get_db
from core.balance import (
    WORLD, WORLD_NODES, ENCOUNTER_TUNING,
    get_physique_config, ARTIFACTS
)
from models.user import User
from models.world import WorldNode
from schemas.world import (
    NodeInfo, NeighborNode, MapResponse, TravelRequest, TravelResponse,
    ExploreRequest, ExploreResponse
)
from services import world_engine
from services.inventory_service import add_item
from api.routes_cultivator import _get_user_or_404

router = APIRouter()

EQUIP_SLOT_COLUMNS = {"weapon": "equipped_weapon", "armor": "equipped_armor",
                      "talisman": "equipped_talisman", "banner": "equipped_banner"}


async def _load_node(db: AsyncSession, node_id: str) -> WorldNode:
    result = await db.execute(select(WorldNode).where(WorldNode.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail=f"Unknown world node '{node_id}'.")
    return node


def _node_info(node: WorldNode) -> NodeInfo:
    return NodeInfo(
        id=node.id, name=node.name, region=node.region, plane=node.plane,
        spirit_density=node.spirit_density, elemental_bias=node.elemental_bias,
        danger_tier=node.danger_tier, description=node.description
    )


@router.get("/map/{discord_id}", response_model=MapResponse)
async def get_map(discord_id: str, db: AsyncSession = Depends(get_db)):
    """Your position in the world and every path open to you."""
    user = await _get_user_or_404(discord_id, db)
    current = await _load_node(db, user.current_node_id or WORLD["starting_node"])

    neighbors = []
    for nid in current.connected_node_ids or []:
        n = await _load_node(db, nid)
        _, cooldown = world_engine.travel_cost(current.id, nid)
        neighbors.append(NeighborNode(
            id=n.id, name=n.name, region=n.region, danger_tier=n.danger_tier,
            travel_cooldown_minutes=cooldown,
            qi_cost_pct=WORLD["travel_qi_cost_pct"]
        ))

    return MapResponse(
        discord_id=user.discord_id,
        current_node=_node_info(current),
        neighbors=neighbors,
        travel_locked_until=user.travel_locked_until,
        message=f"You stand at {current.name}. {current.description}"
    )


@router.post("/travel/{discord_id}", response_model=TravelResponse)
async def travel(discord_id: str, payload: TravelRequest, db: AsyncSession = Depends(get_db)):
    """Journeys to an adjacent node. Costs Qi; the road takes time."""
    user = await _get_user_or_404(discord_id, db)

    if user.is_dead or user.soul_state != "ALIVE":
        raise HTTPException(status_code=400, detail="Only the living may walk the world.")
    if user.active_tribulation:
        raise HTTPException(status_code=400, detail="You cannot flee a Heavenly Tribulation. Face it via /api/tribulation/action.")

    now = datetime.now(timezone.utc)
    if user.travel_locked_until and user.travel_locked_until.tzinfo is None:
        user.travel_locked_until = user.travel_locked_until.replace(tzinfo=timezone.utc)
    if user.travel_locked_until and user.travel_locked_until > now:
        remaining = (user.travel_locked_until - now).total_seconds() / 60.0
        return TravelResponse(success=False, message=f"🚶 You are still on the road ({remaining:.0f} min remaining).",
                              current_node_id=user.current_node_id, arrival_unlock_at=user.travel_locked_until)

    if not world_engine.are_connected(user.current_node_id, payload.target_node_id):
        raise HTTPException(status_code=400, detail="No road leads there from your position. Check /api/world/map.")

    dest = await _load_node(db, payload.target_node_id)
    qi_pct, cooldown = world_engine.travel_cost(user.current_node_id, payload.target_node_id)
    qi_cost = user.max_energy * qi_pct
    if user.spirit_energy < qi_cost:
        raise HTTPException(status_code=400, detail=f"Not enough Qi for the journey (need {qi_cost:.0f}). Meditate first.")

    user.spirit_energy -= qi_cost
    user.current_node_id = dest.id
    user.travel_locked_until = datetime.now(timezone.utc).replace(
        microsecond=0) + __import__("datetime").timedelta(minutes=cooldown)

    await db.commit()
    await db.refresh(user)

    return TravelResponse(
        success=True,
        message=f"🧭 You journey to {dest.name} ({dest.region}, Danger {dest.danger_tier}). "
                f"Spirit density here: ×{dest.spirit_density:.1f}.",
        current_node_id=dest.id,
        arrival_unlock_at=user.travel_locked_until
    )


@router.post("/explore/{discord_id}", response_model=ExploreResponse)
async def explore(discord_id: str, payload: ExploreRequest, db: AsyncSession = Depends(get_db)):
    """
    Explores your current node: herb finds, mineral veins, wandering caravans,
    ancient cave gambles, and demonic ambushes. Cooldown-gated.
    """
    import random as _random
    user = await _get_user_or_404(discord_id, db)

    if user.is_dead or user.soul_state != "ALIVE":
        raise HTTPException(status_code=400, detail="Only the living may roam the wilds.")
    if user.active_tribulation:
        raise HTTPException(status_code=400, detail="Heaven's lightning owns this moment. Face your tribulation.")

    now = datetime.now(timezone.utc)
    if user.last_gathered and user.last_gathered.tzinfo is None:
        user.last_gathered = user.last_gathered.replace(tzinfo=timezone.utc)
    if user.last_gathered:
        elapsed = (now - user.last_gathered).total_seconds() / 60.0
        if elapsed < WORLD["explore_cooldown_minutes"]:
            remaining = round(WORLD["explore_cooldown_minutes"] - elapsed, 1)
            return ExploreResponse(encounter="NOTHING", cooldown_minutes=remaining,
                                   message=f"🧘 You have only just returned from the wilds. Wait {remaining:.0f} more minutes.")

    node = await _load_node(db, user.current_node_id)
    user.last_gathered = now
    rng = _random.Random()

    encounter = world_engine.roll_encounter({"danger_tier": node.danger_tier}, rng)
    details: dict = {}

    if encounter == "herb_find":
        found = world_engine.find_herb(user.realm, node.danger_tier, user.luck_stat, rng)
        await add_item(db, user, found["item"]["id"], found["qty"])
        details = {"item_id": found["item"]["id"], "qty": found["qty"]}
        message = f"🌿 Amid {node.name}'s wilds you gather {found['item']['name']} x{found['qty']}."

    elif encounter == "mineral_vein":
        found = world_engine.find_mineral(node.danger_tier, user.realm, rng)
        await add_item(db, user, found["item"]["id"], found["qty"])
        details = {"item_id": found["item"]["id"], "qty": found["qty"]}
        message = f"⛏️ A glinting vein! You pry loose {found['item']['name']} x{found['qty']}."

    elif encounter == "wandering_caravan":
        from services.economy_engine import daily_stock
        stock = daily_stock(realm_gate=min(16, user.realm + 2))
        details = {"stalls": stock}
        message = ("🐫 A WANDERING CARAVAN! Merchants unfurl their wares on the roadside — "
                   + ", ".join(s["name"] for s in stock) + ". Trade via /api/economy while they linger.")

    elif encounter == "ancient_cave":
        gamble = world_engine.resolve_cave_gamble(node.danger_tier, user.luck_stat, rng)
        if gamble["success"]:
            user.dao_insight += gamble["insight"]
            user.bottleneck_comprehension = min(10.0, user.bottleneck_comprehension + gamble["insight"])
            user.spirit_stones += gamble["stones"]
            if gamble["reward_item"]:
                await add_item(db, user, gamble["reward_item"]["id"], 1)
                details["reward_item"] = gamble["reward_item"]["id"]
        else:
            user.meridian_damage = min(1.0, user.meridian_damage + gamble["meridian_damage"])
            user.spirit_energy = max(0.0, user.spirit_energy * (1.0 - gamble["qi_loss_ratio"]))
        details.update({k: v for k, v in gamble.items() if k != "message"})
        message = gamble["message"]

    elif encounter == "ambush":
        equipped_power = sum(
            ARTIFACTS[getattr(user, col)]["power"]
            for col in EQUIP_SLOT_COLUMNS.values()
            if getattr(user, col) and getattr(user, col) in ARTIFACTS
        )
        stage_index = 0
        from models.realm import get_stages_for_realm
        stages = get_stages_for_realm(user.realm)
        if user.stage in stages:
            stage_index = stages.index(user.stage)
        player_power = world_engine.compute_player_power(
            realm=user.realm, stage_index=stage_index,
            equipped_artifact_powers=equipped_power,
            physique_tier=get_physique_config(user.physique_name)["tier"],
            luck_stat=user.luck_stat
        )
        choice = payload.ambush_choice
        if choice not in ("fight", "flee"):
            choice = "fight" if player_power > node.danger_tier * ENCOUNTER_TUNING["enemy_power_per_danger"] else "flee"
        clash = world_engine.resolve_ambush(player_power, node.danger_tier, user.spirit_stones, choice, rng)
        if clash["result"] == "VICTORY":
            user.spirit_stones += clash["loot_stones"]
            details["loot_stones"] = clash["loot_stones"]
        elif clash["result"] == "DEFEAT":
            user.meridian_damage = min(1.0, user.meridian_damage + clash["meridian_damage"])
            user.spirit_stones = max(0, user.spirit_stones - clash["lost_stones"])
            details.update({"meridian_damage": clash["meridian_damage"], "lost_stones": clash["lost_stones"]})
        details["choice"] = choice
        details["player_power"] = player_power
        message = clash["message"]

    else:
        message = f"🍂 You comb {node.name} for hours but the land keeps its secrets today."

    await db.commit()
    await db.refresh(user)

    return ExploreResponse(
        encounter=encounter.upper(),
        message=message,
        details=details,
        cooldown_minutes=WORLD["explore_cooldown_minutes"]
    )
