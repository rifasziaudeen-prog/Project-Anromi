from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from core.database import get_db
from core.balance import ECONOMY, ITEMS_REGISTRY, MERCHANT_STOCK_POOL
from models.user import User
from schemas.inventory import (
    MerchantResponse, MerchantStall, BuyRequest, SellRequest,
    TradeResponse, ConvertRequest
)
from services.economy_engine import (
    daily_stock, buy_price, sell_price, plan_charge
)
from services.inventory_service import (
    add_item, remove_item, count_item
)
from api.routes_cultivator import _get_user_or_404

router = APIRouter()

GRADE_MAP = {
    "mid": ("mid_grade_stones", 100),
    "high": ("high_grade_stones", 10000),
    "top": ("top_grade_stones", 1000000),
}


@router.get("/merchant/{discord_id}", response_model=MerchantResponse)
async def get_merchant(discord_id: str, db: AsyncSession = Depends(get_db)):
    """
    The Wandering Merchant Pavilion. Stock rotates daily at UTC midnight —
    the SAME stalls for everyone. Miss a treasure and it may be gone tomorrow.
    """
    user = await _get_user_or_404(discord_id, db)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stock = daily_stock(today, realm_gate=min(16, user.realm + 2))
    return MerchantResponse(
        date_utc=today,
        stalls=[MerchantStall(**s) for s in stock],
        message="🛒 The merchant's eyes glitter: 'Fresh wares today only, honored cultivator.'"
    )


@router.post("/buy/{discord_id}", response_model=TradeResponse)
async def buy_item(discord_id: str, payload: BuyRequest, db: AsyncSession = Depends(get_db)):
    """Buys from today's pavilion. Pays with wallet stones, auto-breaking higher grades if short."""
    user = await _get_user_or_404(discord_id, db)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stock_ids = {s["item_id"] for s in daily_stock(today, realm_gate=16)}
    if payload.item_id not in stock_ids:
        raise HTTPException(status_code=400, detail="The merchant does not carry that item today.")
    item_def = ITEMS_REGISTRY[payload.item_id]
    pool_entry = next((e for e in MERCHANT_STOCK_POOL if e["item_id"] == payload.item_id), None)
    if pool_entry and user.realm < pool_entry["min_realm"]:
        raise HTTPException(status_code=400, detail="Your realm is too low; the merchant refuses to sell.")

    cost = buy_price(payload.item_id)
    mid = await count_item(db, user, "mid_grade_stones")
    high = await count_item(db, user, "high_grade_stones")
    top = await count_item(db, user, "top_grade_stones")

    plan = plan_charge(user.spirit_stones, mid, high, top, cost)
    if not plan["ok"]:
        raise HTTPException(status_code=400, detail=plan["message"])

    user.spirit_stones = plan["change_low"]
    for grade_key, delta in (("mid_grade_stones", plan["mid_delta"]),
                             ("high_grade_stones", plan["high_delta"]),
                             ("top_grade_stones", plan["top_delta"])):
        if delta < 0:
            await remove_item(db, user, grade_key, abs(delta))

    await add_item(db, user, payload.item_id, 1)
    await db.commit()
    await db.refresh(user)

    return TradeResponse(
        success=True,
        message=f"You purchase the {item_def['name']} for {cost} low-grade stones (change returned).",
        spirit_stones=user.spirit_stones
    )


@router.post("/sell/{discord_id}", response_model=TradeResponse)
async def sell_item(discord_id: str, payload: SellRequest, db: AsyncSession = Depends(get_db)):
    """Sells owned items to the pavilion at a discount. High-grade pills fetch premiums."""
    user = await _get_user_or_404(discord_id, db)
    item_def = ITEMS_REGISTRY.get(payload.item_id)
    if not item_def:
        raise HTTPException(status_code=404, detail="Unknown item.")
    if item_def.get("category") == "Currency":
        raise HTTPException(status_code=400, detail="Use /convert to exchange spirit stone grades.")
    if not await remove_item(db, user, payload.item_id, payload.quantity):
        raise HTTPException(status_code=400, detail="You do not own enough of that item.")

    unit = sell_price(payload.item_id, payload.quality)
    proceeds = unit * payload.quantity
    user.spirit_stones += proceeds
    await db.commit()
    await db.refresh(user)

    quality_note = f" ({payload.quality} grade)" if payload.quality else ""
    return TradeResponse(
        success=True,
        message=f"Sold {payload.quantity}x {item_def['name']}{quality_note} for {proceeds} low-grade stones.",
        spirit_stones=user.spirit_stones
    )


@router.post("/convert/{discord_id}", response_model=TradeResponse)
async def convert_stones(discord_id: str, payload: ConvertRequest, db: AsyncSession = Depends(get_db)):
    """
    Condenses or splits spirit stones between grades.
    up:   consumes (grade_value × amount) low stones from the wallet → +amount units of that grade in inventory.
    down: consumes amount units of that grade from inventory → wallet += (grade_value × amount) low stones.
    """
    user = await _get_user_or_404(discord_id, db)
    if payload.grade not in GRADE_MAP:
        raise HTTPException(status_code=400, detail="Grade must be mid / high / top.")
    grade_item, equiv_per_unit = GRADE_MAP[payload.grade]
    ratio = ECONOMY["conversion_ratio"]  # one step per call

    if payload.direction == "up":
        cost = ratio * payload.amount  # e.g., 1 Mid per 100 low per step
        # For higher grades, chain through the equivalent value instead
        steps_value = {"mid": 100, "high": 10000, "top": 1000000}[payload.grade]
        total_needed = steps_value * payload.amount
        if user.spirit_stones < total_needed:
            raise HTTPException(status_code=400, detail=f"Need {total_needed} low-grade stones to condense that much.")
        user.spirit_stones -= total_needed
        await add_item(db, user, grade_item, payload.amount)
        await db.commit()
        await db.refresh(user)
        return TradeResponse(success=True, message=f"Condensed {total_needed} low stones → {payload.amount}x {ITEMS_REGISTRY[grade_item]['name']}.",
                             spirit_stones=user.spirit_stones)
    elif payload.direction == "down":
        if not await remove_item(db, user, grade_item, payload.amount):
            raise HTTPException(status_code=400, detail="You do not own enough of that grade.")
        gained = equiv_per_unit * payload.amount
        user.spirit_stones += gained
        await db.commit()
        await db.refresh(user)
        return TradeResponse(success=True, message=f"Crunched {payload.amount}x {ITEMS_REGISTRY[grade_item]['name']} → +{gained} low-grade stones.",
                             spirit_stones=user.spirit_stones)
    else:
        raise HTTPException(status_code=400, detail="Direction must be 'up' or 'down'.")
