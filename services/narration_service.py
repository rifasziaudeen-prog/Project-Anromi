"""
Narration Service — "The Heavenly Dao" speaks through free-tier LLMs.

All supported providers expose OpenAI-compatible chat completions:
  groq       → https://api.groq.com/openai/v1/chat/completions
  gemini     → https://generativelanguage.googleapis.com/v1beta/openai/chat/completions
  openrouter → https://openrouter.ai/api/v1/chat/completions

Behavior:
- Provider priority comes from .env (NARRATION_PROVIDERS), first configured wins.
- Rate limits / errors / timeouts automatically fall through to the next provider.
- If NO provider is configured (or all fail), canned fallback lines keep the
  game fully playable — narration is enhancement, never a dependency.
Keys/models live ONLY in .env; the persona voice lives in core/balance.NARRATION.
"""
import httpx
import logging
from typing import Dict, Any, List

from core.config import settings
from core.balance import NARRATION

log = logging.getLogger("anromi.narration")

PROVIDER_ENDPOINTS = {
    "groq": "https://api.groq.com/openai/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
}


class _SafeFormat(dict):
    """Template formatting that tolerates missing context keys."""
    def __missing__(self, key: str) -> str:
        return ""


def build_provider_chain() -> List[Dict[str, str]]:
    """
    Ordered attempt list: every configured (provider, model) pair, expanded
    from each provider's MODELS list — so a dead/rate-limited model falls
    through to the next model of the same provider before switching providers.
    Skips providers without API keys.
    """
    keys = {
        "groq": settings.GROQ_API_KEY,
        "gemini": settings.GEMINI_API_KEY,
        "openrouter": settings.OPENROUTER_API_KEY,
    }
    # Common credential mix-ups caught early with actionable hints
    if keys["gemini"] and keys["gemini"].startswith("AQ."):
        log.warning(
            "GEMINI_API_KEY looks like an ephemeral OAuth token ('AQ....' prefix), "
            "NOT an AI Studio API key. Get a persistent key at https://aistudio.google.com/apikey "
            "(it should start with 'AIza')."
        )
    model_lists = {
        "groq": [m.strip() for m in settings.GROQ_MODELS.split(",") if m.strip()],
        "gemini": [m.strip() for m in settings.GEMINI_MODELS.split(",") if m.strip()],
        "openrouter": [m.strip() for m in settings.OPENROUTER_MODELS.split(",") if m.strip()],
    }
    chain = []
    for raw in settings.NARRATION_PROVIDERS.split(","):
        name = raw.strip().lower()
        if not name or name not in PROVIDER_ENDPOINTS:
            continue
        if not keys.get(name):
            continue
        for model in model_lists.get(name) or [""]:
            chain.append({
                "name": name,
                "key": keys[name],
                "model": model,
                "url": PROVIDER_ENDPOINTS[name],
            })
    return chain


def build_event_prompt(event_type: str, context: Dict[str, Any]) -> str:
    template = NARRATION["event_templates"].get(event_type)
    if not template:
        return (
            f"The cultivator {context.get('username', 'a nameless wanderer')} has done something "
            f"noteworthy ({event_type}). Remark upon it briefly."
        )
    return template.format_map(_SafeFormat(context))


async def generate_narration(event_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tries each configured provider in order. Returns:
      {"narration": str, "provider": str|None, "model": str|None, "fell_back": bool}
    Never raises — failure degrades to a canned line.
    """
    system = NARRATION["system_prompt"]
    user_prompt = build_event_prompt(event_type, context)

    for provider in build_provider_chain():
        try:
            async with httpx.AsyncClient(timeout=settings.NARRATION_TIMEOUT_SECONDS) as client:
                resp = await client.post(
                    provider["url"],
                    headers={
                        "Authorization": f"Bearer {provider['key']}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": provider["model"],
                        "messages": [
                            {"role": "system", "content": system},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": NARRATION["temperature"],
                        "max_tokens": NARRATION["max_tokens"],
                    },
                )
            if resp.status_code == 200:
                data = resp.json()
                text = (data["choices"][0]["message"]["content"] or "").strip()
                if text:
                    return {"narration": text, "provider": provider["name"],
                            "model": provider["model"], "fell_back": False}
            log.warning(
                "Narration provider '%s' failed: HTTP %s %s",
                provider["name"], resp.status_code, resp.text[:160]
            )
        except Exception as ex:
            log.warning("Narration provider '%s' raised: %s", provider["name"], ex)
            continue  # rate limit, timeout, bad model id → next provider

    log.warning("All narration providers exhausted — using fallback line for '%s'.", event_type)

    fallback = NARRATION["fallback_lines"].get(event_type, "The Dao is silent... for now.")
    return {"narration": fallback, "provider": None, "model": None, "fell_back": True}


def available_providers() -> List[str]:
    return [p["name"] for p in build_provider_chain()]
