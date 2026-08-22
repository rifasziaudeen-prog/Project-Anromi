"""
Event Service — append-only world chronicle.
Routes log major moments here; the Discord announcer and narration
context read from it. Pure DB helpers.
"""
import json
from typing import Dict, Any, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.events import GameEvent


async def log_event(db: AsyncSession, discord_id: str, username: str,
                    event_type: str, payload: Optional[Dict[str, Any]] = None) -> GameEvent:
    event = GameEvent(
        discord_id=discord_id,
        username=username or "",
        event_type=event_type,
        payload=json.dumps(payload or {}, ensure_ascii=False, default=str),
    )
    db.add(event)
    await db.flush()
    return event


async def get_recent_events(db: AsyncSession, since_id: int = 0, limit: int = 50) -> List[GameEvent]:
    stmt = (
        select(GameEvent)
        .where(GameEvent.id > since_id)
        .order_by(GameEvent.id.asc())
        .limit(max(1, min(limit, 200)))
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


def event_to_dict(event: GameEvent) -> Dict[str, Any]:
    try:
        payload = json.loads(event.payload or "{}")
    except (ValueError, TypeError):
        payload = {}
    return {
        "id": event.id,
        "discord_id": event.discord_id,
        "username": event.username,
        "event_type": event.event_type,
        "payload": payload,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }
