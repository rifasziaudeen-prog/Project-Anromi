"""
Thin aiohttp wrapper around the Anromi FastAPI.
ZERO game logic lives here — every method maps 1:1 to an HTTP endpoint.
"""
import aiohttp
from typing import Optional, Dict, Any


class ApiError(Exception):
    def __init__(self, status: int, detail: str):
        self.status = status
        self.detail = detail
        super().__init__(f"[{status}] {detail}")


class AnromiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        if not self._session:
            self._session = aiohttp.ClientSession()

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def _req(self, method: str, path: str, params: Dict = None, json_body: Dict = None) -> Any:
        await self.start()
        url = f"{self.base_url}{path}"
        async with self._session.request(method, url, params=params, json=json_body) as resp:
            data = await resp.json(content_type=None)
            if resp.status >= 400:
                detail = data.get("detail", str(data)) if isinstance(data, dict) else str(data)
                raise ApiError(resp.status, str(detail))
            return data

    # ── Cultivator ──
    async def register(self, discord_id: str, username: str):
        return await self._req("POST", "/api/cultivator/register",
                               json_body={"discord_id": discord_id, "username": username})

    async def profile(self, discord_id: str):
        return await self._req("GET", f"/api/cultivator/profile/{discord_id}")

    async def meditate(self, discord_id: str):
        return await self._req("POST", f"/api/cultivator/meditate/{discord_id}")

    async def breakthrough_odds(self, discord_id: str):
        return await self._req("GET", f"/api/cultivator/breakthrough-odds/{discord_id}")

    async def breakthrough(self, discord_id: str, pill_bonus: float = 0.0):
        return await self._req("POST", f"/api/cultivator/breakthrough/{discord_id}",
                               json_body={"pill_bonus": pill_bonus})

    async def dao_heart(self, discord_id: str):
        return await self._req("GET", f"/api/cultivator/dao-heart/{discord_id}")

    # ── Soul ──
    async def soul_state(self, discord_id: str):
        return await self._req("GET", f"/api/soul/state/{discord_id}")

    async def possess(self, discord_id: str, target_name: str, target_strength: float):
        return await self._req("POST", f"/api/soul/possess/{discord_id}",
                               json_body={"target_name": target_name, "target_strength": target_strength})

    async def reincarnate(self, discord_id: str):
        return await self._req("POST", f"/api/soul/reincarnate/{discord_id}")

    # ── Inventory / Alchemy / Forging ──
    async def bag(self, discord_id: str):
        return await self._req("GET", f"/api/inventory/bag/{discord_id}")

    async def consume(self, discord_id: str, item_id: str, quality: Optional[str] = None):
        body: Dict[str, Any] = {"item_id": item_id}
        if quality:
            body["quality"] = quality
        return await self._req("POST", f"/api/inventory/consume/{discord_id}", json_body=body)

    async def recipes(self, discord_id: str):
        return await self._req("GET", f"/api/alchemy/recipes/{discord_id}")

    async def refine(self, discord_id: str, recipe_id: str,
                     furnace: str = "furnace_mortal_iron", flame: str = "flame_wood"):
        return await self._req("POST", f"/api/alchemy/refine/{discord_id}",
                               json_body={"recipe_id": recipe_id, "furnace_item_id": furnace,
                                          "flame_item_id": flame})

    async def craft(self, discord_id: str, artifact_id: str):
        return await self._req("POST", f"/api/forging/craft/{discord_id}",
                               json_body={"artifact_id": artifact_id})

    async def equip(self, discord_id: str, slot: str, item_id: Optional[str] = None):
        return await self._req("POST", f"/api/forging/equip/{discord_id}",
                               json_body={"slot": slot, "item_id": item_id})

    async def blueprints(self):
        return await self._req("GET", "/api/forging/blueprints")

    # ── Economy ──
    async def merchant(self, discord_id: str):
        return await self._req("GET", f"/api/economy/merchant/{discord_id}")

    async def buy(self, discord_id: str, item_id: str):
        return await self._req("POST", f"/api/economy/buy/{discord_id}", json_body={"item_id": item_id})

    async def sell(self, discord_id: str, item_id: str, quantity: int, quality: Optional[str] = None):
        body: Dict[str, Any] = {"item_id": item_id, "quantity": quantity}
        if quality:
            body["quality"] = quality
        return await self._req("POST", f"/api/economy/sell/{discord_id}", json_body=body)

    async def convert(self, discord_id: str, direction: str, grade: str, amount: int):
        return await self._req("POST", f"/api/economy/convert/{discord_id}",
                               json_body={"direction": direction, "grade": grade, "amount": amount})

    # ── World ──
    async def map(self, discord_id: str):
        return await self._req("GET", f"/api/world/map/{discord_id}")

    async def travel(self, discord_id: str, target_node_id: str):
        return await self._req("POST", f"/api/world/travel/{discord_id}",
                               json_body={"target_node_id": target_node_id})

    async def explore(self, discord_id: str, ambush_choice: Optional[str] = None):
        body: Dict[str, Any] = {}
        if ambush_choice:
            body["ambush_choice"] = ambush_choice
        return await self._req("POST", f"/api/world/explore/{discord_id}", json_body=body)

    # ── Tribulation ──
    async def tribulation_state(self, discord_id: str):
        return await self._req("GET", f"/api/tribulation/state/{discord_id}")

    async def tribulation_initiate(self, discord_id: str):
        return await self._req("POST", f"/api/tribulation/initiate/{discord_id}")

    async def tribulation_action(self, discord_id: str, action: str):
        return await self._req("POST", f"/api/tribulation/action/{discord_id}",
                               json_body={"action": action})

    # ── Narration & Events ──
    async def narrate(self, discord_id: str, event_type: str, extra: Optional[Dict] = None):
        return await self._req("POST", f"/api/narration/narrate/{discord_id}",
                               json_body={"event_type": event_type, "extra": extra or {}})

    async def recent_events(self, since_id: int = 0, limit: int = 50):
        return await self._req("GET", "/api/narration/events/recent",
                               params={"since_id": since_id, "limit": limit})
