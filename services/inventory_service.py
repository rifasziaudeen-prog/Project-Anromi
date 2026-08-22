"""
Inventory DB helpers. Item definitions live in core/balance.py;
this module only manipulates ownership stacks.
"""
from typing import Optional, Dict, Any, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from core.balance import ITEMS_REGISTRY
from models.inventory import InventoryEntry
from models.user import User


def get_item_def(item_id: str) -> Optional[Dict[str, Any]]:
    return ITEMS_REGISTRY.get(item_id)


async def list_bag(db: AsyncSession, user: User) -> List[InventoryEntry]:
    stmt = select(InventoryEntry).where(
        InventoryEntry.user_id == user.id,
        InventoryEntry.quantity > 0
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


def _stack_filters(user_id: int, item_id: str, quality: Optional[str]):
    filters = [
        InventoryEntry.user_id == user_id,
        InventoryEntry.item_id == item_id,
    ]
    if quality is None:
        filters.append(InventoryEntry.quality.is_(None))
    else:
        filters.append(InventoryEntry.quality == quality)
    return filters


async def count_item(db: AsyncSession, user: User, item_id: str, quality: Optional[str] = None) -> int:
    """Sums across all matching stacks (robust to duplicate NULL-quality rows)."""
    stmt = select(func.coalesce(func.sum(InventoryEntry.quantity), 0)).where(
        *_stack_filters(user.id, item_id, quality)
    )
    result = await db.execute(stmt)
    return int(result.scalar() or 0)


async def add_item(db: AsyncSession, user: User, item_id: str, qty: int, quality: Optional[str] = None) -> InventoryEntry:
    result = await db.execute(
        select(InventoryEntry).where(*_stack_filters(user.id, item_id, quality)).order_by(InventoryEntry.id)
    )
    entry = result.scalars().first()
    if entry:
        entry.quantity += qty
    else:
        entry = InventoryEntry(user_id=user.id, item_id=item_id, quality=quality, quantity=qty)
        db.add(entry)
    await db.flush()
    return entry


async def remove_item(db: AsyncSession, user: User, item_id: str, qty: int, quality: Optional[str] = None) -> bool:
    """Deducts across all matching stacks. Returns False if not enough owned."""
    have = await count_item(db, user, item_id, quality)
    if have < qty:
        return False
    result = await db.execute(
        select(InventoryEntry)
        .where(*_stack_filters(user.id, item_id, quality), InventoryEntry.quantity > 0)
        .order_by(InventoryEntry.id)
    )
    remaining = qty
    for entry in result.scalars().all():
        take = min(entry.quantity, remaining)
        entry.quantity -= take
        remaining -= take
        if remaining <= 0:
            break
    await db.flush()
    return True


async def has_materials(db: AsyncSession, user: User, materials: Dict[str, int]) -> bool:
    for item_id, qty in materials.items():
        if await count_item(db, user, item_id) < qty:
            return False
    return True


async def consume_materials(db: AsyncSession, user: User, materials: Dict[str, int]) -> bool:
    if not await has_materials(db, user, materials):
        return False
    for item_id, qty in materials.items():
        await remove_item(db, user, item_id, qty)
    return True


GRADE_ORDER = ["Flawless", "Top", "Medium", "Low"]  # best-first; consumption picks by default order


async def find_pill_stack(db: AsyncSession, user: User, item_id: str, quality: Optional[str] = None) -> Optional[InventoryEntry]:
    """
    Finds a pill stack: exact grade if given, otherwise the LOWEST grade first
    (players burn their worst pills first).
    """
    if quality is not None:
        stmt = select(InventoryEntry).where(
            InventoryEntry.user_id == user.id,
            InventoryEntry.item_id == item_id,
            InventoryEntry.quality == quality,
            InventoryEntry.quantity > 0
        ).order_by(InventoryEntry.id)
        result = await db.execute(stmt)
        return result.scalars().first()
    for grade in reversed(GRADE_ORDER):  # Low → Flawless
        stmt = select(InventoryEntry).where(
            InventoryEntry.user_id == user.id,
            InventoryEntry.item_id == item_id,
            InventoryEntry.quality == grade,
            InventoryEntry.quantity > 0
        ).order_by(InventoryEntry.id)
        result = await db.execute(stmt)
        entry = result.scalars().first()
        if entry:
            return entry
    return None


async def owns_item(db: AsyncSession, user: User, item_id: str) -> bool:
    return await count_item(db, user, item_id) > 0
