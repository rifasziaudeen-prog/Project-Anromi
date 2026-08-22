import pytest
import asyncio
from typing import Dict, Any

from core.config import settings
from core.balance import NARRATION
from services.narration_service import (
    build_provider_chain,
    build_event_prompt,
    generate_narration,
    _SafeFormat,
)
from services.event_service import log_event, get_recent_events, event_to_dict


def _force_settings(monkeypatch: pytest.MonkeyPatch, providers: str,
                    groq: str = "", gemini: str = "", openrouter: str = "",
                    groq_models: str = "g-model-a,g-model-b",
                    gemini_models: str = "gm-model-a",
                    openrouter_models: str = "o-model-a"):
    monkeypatch.setattr(settings, "NARRATION_PROVIDERS", providers)
    monkeypatch.setattr(settings, "GROQ_API_KEY", groq)
    monkeypatch.setattr(settings, "GEMINI_API_KEY", gemini)
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", openrouter)
    monkeypatch.setattr(settings, "GROQ_MODELS", groq_models)
    monkeypatch.setattr(settings, "GEMINI_MODELS", gemini_models)
    monkeypatch.setattr(settings, "OPENROUTER_MODELS", openrouter_models)


def test_provider_chain_respects_priority_and_skips_empty_keys(monkeypatch):
    _force_settings(monkeypatch, "groq,gemini,openrouter", groq="K1")
    chain = build_provider_chain()
    assert [p["name"] for p in chain] == ["groq", "groq"]
    assert [p["model"] for p in chain] == ["g-model-a", "g-model-b"]

    _force_settings(monkeypatch, "groq,gemini,openrouter", gemini="G1", openrouter="O1")
    chain = build_provider_chain()
    assert [p["name"] for p in chain] == ["gemini", "openrouter"]

    _force_settings(monkeypatch, "openrouter,groq", openrouter="O1", groq="K1")
    chain = build_provider_chain()
    assert chain[0]["name"] == "openrouter"   # env order wins
    assert chain[-1]["name"] == "groq"


def test_default_model_lists_use_current_2026_ids():
    assert settings.GROQ_MODELS.startswith("openai/gpt-oss-120b")
    assert "openai/gpt-oss-20b" in settings.GROQ_MODELS
    assert "groq/compound-mini" in settings.GROQ_MODELS
    assert settings.GEMINI_MODELS.split(",")[0] == "gemini-3.7-flash"
    assert "gemini-3.6-flash" in settings.GEMINI_MODELS


def test_provider_chain_empty_when_no_keys(monkeypatch):
    _force_settings(monkeypatch, "groq,gemini,openrouter")
    assert build_provider_chain() == []


def test_event_prompt_formats_known_placeholders():
    ctx = {"username": "Han Li", "realm_name_en": "Nascent Soul", "stage": "Layer 1",
           "dao_title": "Soul Monarch"}
    prompt = build_event_prompt("breakthrough", ctx)
    assert "Han Li" in prompt and "Nascent Soul" in prompt

def test_event_prompt_tolerates_missing_keys():
    prompt = build_event_prompt("breakthrough", {"username": "Nobody"})
    assert "Nobody" in prompt  # missing keys render empty, never raise

def test_unknown_event_gets_generic_prompt():
    prompt = build_event_prompt("totally_new_thing", {"username": "X"})
    assert "X" in prompt and "totally_new_thing" in prompt

def test_narration_falls_back_without_providers(monkeypatch):
    _force_settings(monkeypatch, "groq,gemini,openrouter")  # no keys at all

    async def run():
        return await generate_narration("breakthrough", {"username": "Lonely Daoist"})

    result = asyncio.run(run())
    assert result["fell_back"] is True
    assert result["provider"] is None
    assert result["narration"] == NARRATION["fallback_lines"]["breakthrough"]


# ── Event chronicle (real async SQLite, in-memory) ────────────────────

async def _fresh_session():
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from core.database import Base
    import models.events  # register table
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def test_event_log_roundtrip():
    async def run() -> Dict[str, Any]:
        Session = await _fresh_session()
        async with Session() as db:
            e1 = await log_event(db, "user-1", "Han Li", "breakthrough", {"realm": 4})
            await log_event(db, "user-2", "Rival", "true_death", {"legacy_awarded": 12})
            await db.commit()
            events = await get_recent_events(db, since_id=0)
            newer = await get_recent_events(db, since_id=e1.id)
            return {
                "count": len(events),
                "first": event_to_dict(events[0]),
                "newer_count": len(newer),
            }

    out = asyncio.run(run())
    assert out["count"] == 2
    assert out["first"]["event_type"] == "breakthrough"
    assert out["first"]["payload"]["realm"] == 4
    assert out["newer_count"] == 1  # since_id filtering works

def test_event_payload_survives_bad_json():
    from models.events import GameEvent
    bad = GameEvent(discord_id="x", username="y", event_type="z", payload="not json{")
    d = event_to_dict(bad)
    assert d["payload"] == {}
