"""
Economy Engine — spirit stone grades, merchant barter, daily rotation.

Wallet: User.spirit_stones holds LOW-grade stones. Mid/High/Top grades are
inventory currency items (see ECONOMY["currency_items"], 100:1 chain).
Merchant stock is seeded by UTC date → same stalls for everyone that day
(deterministic FOMO). All tunables in balance → ECONOMY.
"""
import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from core.balance import (
    ECONOMY,
    MERCHANT_STOCK_POOL,
    ITEMS_REGISTRY,
)


# ── Pricing ─────────────────────────────────────────────────────────

def buy_price(item_id: str) -> int:
    item = ITEMS_REGISTRY[item_id]
    return max(1, int(round(item["base_price"] * ECONOMY["buy_markup"])))


def sell_price(item_id: str, quality: Optional[str] = None) -> int:
    item = ITEMS_REGISTRY.get(item_id)
    if not item:
        return 0
    price = item["base_price"] * ECONOMY["sell_ratio"]
    if quality:
        price *= ECONOMY["merchant_sell_grade_mult"].get(quality, 1.0)
    return max(1, int(round(price)))


def convert_stones(amount: int, direction: str) -> Tuple[bool, int, str]:
    """
    direction "up": low wallet → higher-grade inventory items (returns count of high units).
    direction "down": high-grade unit count → low stones.
    Only one grade step per call; chains handled by repeated calls/routes.
    """
    ratio = ECONOMY["conversion_ratio"]
    if direction == "up":
        if amount < ratio:
            return False, 0, f"Need at least {ratio} low-grade stones to condense upward."
        return True, amount // ratio, ""
    elif direction == "down":
        return True, amount * ratio, ""
    return False, 0, "Direction must be 'up' or 'down'."


# ── Daily Merchant ──────────────────────────────────────────────────

def merchant_seed(date_str: Optional[str] = None) -> int:
    d = date_str or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stable_hash = 0
    for ch in d:
        stable_hash = (stable_hash * 131 + ord(ch)) % (10 ** 9 + 7)
    return stable_hash


def daily_stock(date_str: Optional[str] = None, realm_gate: int = 16) -> List[Dict[str, Any]]:
    """
    Deterministic daily stalls: same seed → same stock for ALL players today.
    realm_gate filters what a given cultivator may SEE (higher realms unlock more).
    """
    rng = random.Random(merchant_seed(date_str))
    pool = [e for e in MERCHANT_STOCK_POOL if e["min_realm"] <= realm_gate]
    slots = min(ECONOMY["merchant_daily_slots"], len(pool))
    chosen = []
    pool_copy = list(pool)
    for _ in range(slots):
        weights = [e["weight"] for e in pool_copy]
        entry = rng.choices(pool_copy, weights=weights, k=1)[0]
        pool_copy.remove(entry)
        chosen.append({
            "item_id": entry["item_id"],
            "name": ITEMS_REGISTRY[entry["item_id"]]["name"],
            "price_low_stones": buy_price(entry["item_id"]),
            "stock_left": None,  # unlimited per day; scarcity comes from rotation
        })
    return chosen


# ── Stone charging with automatic grade breakdown ────────────────────

def plan_charge(low_wallet: int, mid_count: int, high_count: int, top_count: int, cost: int) -> Dict[str, Any]:
    """
    Plans payment for `cost` low-stone-equivalents using the wallet plus
    auto-breaking higher grades downward when short.
    Returns the exact wallet/grade deltas to apply, or ok=False.
    """
    total_available = low_wallet + mid_count * 100 + high_count * 10000 + top_count * 1000000
    if total_available < cost:
        return {"ok": False, "message": f"Not enough spirit stones. Need {cost}, have {total_available} low-grade equivalent."}

    # Break down as little as possible: use wallet first
    from_mid = from_high = from_top = 0
    remaining = cost - low_wallet
    if remaining > 0 and top_count > 0:
        need_top = -(-remaining // 1000000)
        use_top = min(top_count, need_top)
        from_top = use_top
        remaining -= use_top * 1000000
    if remaining > 0 and high_count > 0:
        need_high = -(-remaining // 10000)
        use_high = min(high_count, need_high)
        from_high = use_high
        remaining -= use_high * 10000
    if remaining > 0 and mid_count > 0:
        need_mid = -(-remaining // 100)
        use_mid = min(mid_count, need_mid)
        from_mid = use_mid
        remaining -= use_mid * 100
    # Overflow change returns to wallet as low stones
    spent_equiv = cost
    available_equiv_after_breaking = low_wallet + from_mid*100 + from_high*10000 + from_top*1000000
    change = available_equiv_after_breaking - spent_equiv

    new_low = change  # wallet emptied then refunded change
    return {
        "ok": True,
        "wallet_delta": new_low - low_wallet,          # usually negative
        "mid_delta": -from_mid,
        "high_delta": -from_high,
        "top_delta": -from_top,
        "change_low": change,
        "message": "",
    }
