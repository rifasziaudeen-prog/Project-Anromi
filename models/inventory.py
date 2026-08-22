from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime, timezone
from core.database import Base


class InventoryEntry(Base):
    """
    One row per (user, item, quality) stack.
    Item DEFINITIONS live in core/balance.py — this table only tracks ownership,
    so items can be added/retuned without any migration.
    quality: pill grades ("Low"/"Medium"/"Top"/"Flawless"); NULL for non-pills.
    """
    __tablename__ = "inventory_entries"
    __table_args__ = (
        UniqueConstraint("user_id", "item_id", "quality", name="uq_user_item_quality"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    item_id = Column(String, index=True, nullable=False)
    quality = Column(String, nullable=True)   # pills only
    quantity = Column(Integer, default=0, nullable=False)
    acquired_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
