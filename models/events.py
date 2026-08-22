from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone
from core.database import Base


class GameEvent(Base):
    """
    Append-only log of major world moments (breakthroughs, tribulations,
    deaths...). Feeds the Discord announcer and narration context.
    """
    __tablename__ = "game_events"

    id = Column(Integer, primary_key=True, index=True)
    discord_id = Column(String, index=True, nullable=False)
    username = Column(String, default="")
    event_type = Column(String, index=True, nullable=False)
    payload = Column(Text, default="{}")   # JSON blob of event details
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
