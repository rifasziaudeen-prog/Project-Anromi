"""
Anromi Discord Bot — pure API client, zero game logic.
Run the FastAPI server first (uvicorn main:app), then: python run_bot.py
"""
import asyncio
import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

from bot.config import DISCORD_BOT_TOKEN, API_BASE_URL, ANNOUNCE_CHANNEL_ID, ANNOUNCE_POLL_SECONDS
from bot.api_client import AnromiClient, ApiError
from bot.embeds import profile_embed, simple_result_embed, event_embed, tribulation_embed
from bot.views import TribulationView, send_tribulation_status

log = logging.getLogger("anromi.bot")

api = AnromiClient(API_BASE_URL)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

TRIBULATION_ACTIONS = app_commands.Choice


def _user_id(interaction: discord.Interaction) -> str:
    return str(interaction.user.id)


def _err_embed(ex: ApiError) -> discord.Embed:
    return simple_result_embed(False, str(ex.detail))


# ── Core loop ─────────────────────────────────────────────────────────

@bot.event
async def setup_hook():
    await api.start()
    if ANNOUNCE_CHANNEL_ID:
        asyncio.create_task(announcer_loop())
    await bot.tree.sync()
    log.info("Slash commands synced.")


@bot.event
async def on_ready():
    log.info("Anromi bot online as %s", bot.user)


async def announcer_loop():
    """Polls the world chronicle and posts epic moments to the announce channel."""
    await bot.wait_until_ready()
    channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
    if not channel:
        log.warning("ANNOUNCE_CHANNEL_ID %s not found — announcer idle.", ANNOUNCE_CHANNEL_ID)
        return
    last_id = 0
    while not bot.is_closed():
        try:
            data = await api.recent_events(since_id=last_id)
            for ev in data.get("events", []):
                last_id = max(last_id, ev["id"])
                try:
                    await channel.send(embed=event_embed(ev))
                except discord.HTTPException:
                    pass
            last_id = max(last_id, data.get("last_id", last_id))
        except Exception as ex:
            log.debug("announcer poll failed: %s", ex)
        await asyncio.sleep(ANNOUNCE_POLL_SECONDS)


def tribulation_guard(coro_factory):
    async def wrapper(interaction: discord.Interaction, *args):
        await interaction.response.defer()
        try:
            embed = await coro_factory(interaction, *args)
            await interaction.followup.send(embed=embed)
        except ApiError as ex:
            await interaction.followup.send(embed=_err_embed(ex))
    return wrapper


# ── Commands ──────────────────────────────────────────────────────────

@bot.tree.command(name="register", description="Begin your cultivation path")
async def register(interaction: discord.Interaction, username: str):
    await interaction.response.defer()
    try:
        p = await api.register(_user_id(interaction), username[:40])
        root_card = f"Root: {p['spiritual_root']} · Physique: {p['physique_name']}"
        await interaction.followup.send(
            embed=profile_embed(p).set_footer(text=f"Heaven has noticed you. {root_card}"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="stats", description="Inspect a cultivator's full status")
async def stats(interaction: discord.Interaction,
                cultivator: Optional[discord.User] = None):
    await interaction.response.defer()
    target = str((cultivator or interaction.user).id)
    try:
        await interaction.followup.send(embed=profile_embed(await api.profile(target)))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="meditate", description="Gather spiritual Qi")
async def meditate(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        r = await api.meditate(_user_id(interaction))
        e = simple_result_embed(True, r["message"], title="🧘 Meditation")
        e.add_field(name="Streak", value=f"Day {r['streak_days']} ×{r['streak_multiplier']}", inline=True)
        e.add_field(name="Qi", value=f"{r['spirit_energy']:.0f}/{r['max_energy']:.0f}", inline=True)
        if r["can_breakthrough"]:
            e.add_field(name="⚡ Ready", value="Breakthrough possible!", inline=True)
        await interaction.followup.send(embed=e)
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="breakthrough", description="Attempt to shatter your bottleneck")
async def breakthrough(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        odds = await api.breakthrough_odds(_user_id(interaction))
        r = await api.breakthrough(_user_id(interaction))
        if r["outcome"] == "TRIBULATION_REQUIRED":
            state = await api.tribulation_state(_user_id(interaction))
            summary = state.get("summary") or {}
            e = tribulation_embed(summary)
            e.title = "☁️ HEAVEN ANSWERS!"
            await interaction.followup.send(
                content=r["message"][:1500] + "\n\n**Face the storm:**",
                embed=e,
                view=TribulationView(api, _user_id(interaction)))
            return
        color = discord.Color.green() if r["success"] else discord.Color.red()
        e = simple_result_embed(r["success"], r["message"], title="⚡ Breakthrough Attempt")
        e.color = color
        if r.get("needed") is not None:
            e.add_field(name="Roll vs Needed", value=f"{r['roll']:.3f} vs ≤{r['needed']:.3f}", inline=True)
        await interaction.followup.send(embed=e)
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="dao-heart", description="Check Dao Heart stability and karma")
async def dao_heart(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        d = await api.dao_heart(_user_id(interaction))
        await interaction.followup.send(embed=simple_result_embed(True, d["message"],
                                                                  title=f"☯️ Dao Heart: {d['status']} ({d['dao_heart_stability']}/100) · Karma: {d['karma_sin']} ({d['karma_class']})"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="bag", description="Open your spatial pouch")
async def bag(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        b = await api.bag(_user_id(interaction))
        lines = [f"`{x['quantity']:>3}×` **{x['name']}**" + (f" [{x['quality']}]" if x["quality"] else "")
                 for x in b["entries"]]
        e = simple_result_embed(True, "\n".join(lines)[:4000] or "*Empty. The void stares back.*",
                                title=f"🎒 Pouch · {b['spirit_stones']:,} stones · Toxicity {b['pill_toxicity']:.0f}")
        await interaction.followup.send(embed=e)
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="recipes", description="List known pill recipes and craftability")
async def recipes(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        rs = await api.recipes(_user_id(interaction))
        lines = []
        for r in rs["recipes"]:
            mark = "✅" if r["craftable_now"] else "🔒"
            mats = ", ".join(f"{k}×{v}" for k, v in r["materials"].items())
            lines.append(f"{mark} **{r['name']}** (T{r['tier']} · Lv{r['alchemy_level_req']}+)\n> {mats}")
        await interaction.followup.send(embed=simple_result_embed(
            True, "\n".join(lines)[:4000],
            title=f"⚗️ Recipes · Alchemy Lv{rs['alchemy_level']} {rs['alchemy_title']}"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="refine", description="Brew a pill (impurity decides its grade)")
@app_commands.describe(recipe_id="Recipe id, see /recipes", furnace_item_id="Furnace you own",
                       flame_item_id="Flame fuel to burn")
async def refine(interaction: discord.Interaction, recipe_id: str,
                 furnace_item_id: str = "furnace_mortal_iron", flame_item_id: str = "flame_wood"):
    await interaction.response.defer()
    try:
        r = await api.refine(_user_id(interaction), recipe_id, furnace_item_id, flame_item_id)
        m = r["mastery"] or {}
        e = simple_result_embed(True, r["message"], title=f"⚗️ Refining · Grade: {r['grade']} ({r['impurity']}% impurity)")
        if m.get("level"):
            e.add_field(name="Mastery", value=f"Lv{m['level']} {m['title']} ({m['exp']} xp)", inline=True)
        await interaction.followup.send(embed=e)
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="consume", description="Swallow a pill from your pouch")
@app_commands.describe(item_id="Pill id", quality="Exact grade to burn (optional)")
async def consume(interaction: discord.Interaction, item_id: str, quality: Optional[str] = None):
    await interaction.response.defer()
    try:
        r = await api.consume(_user_id(interaction), item_id, quality)
        await interaction.followup.send(embed=simple_result_embed(True, r["message"], title="💊 Consumed"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="craft", description="Forge an artifact (failure eats half the materials)")
async def craft(interaction: discord.Interaction, artifact_id: str):
    await interaction.response.defer()
    try:
        r = await api.craft(_user_id(interaction), artifact_id)
        await interaction.followup.send(embed=simple_result_embed(r["success"], r["message"],
                                                                  title=f"🔨 Forging ({r['chance']:.0%})"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="equip", description="Equip an owned artifact (item_id blank = unequip)")
@app_commands.choices(slot=[
    app_commands.Choice(name="weapon", value="weapon"),
    app_commands.Choice(name="armor", value="armor"),
    app_commands.Choice(name="talisman", value="talisman"),
    app_commands.Choice(name="banner", value="banner"),
])
async def equip(interaction: discord.Interaction, slot: str, item_id: Optional[str] = None):
    await interaction.response.defer()
    try:
        r = await api.equip(_user_id(interaction), slot, item_id)
        await interaction.followup.send(embed=simple_result_embed(True, r["message"], title="🗡️ Equipment"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="map", description="See your location and adjacent paths")
async def map_cmd(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        m = await api.map(_user_id(interaction))
        cur = m["current_node"]
        lines = [
            f"**{n['name']}** — Danger {n['danger_tier']} · `{n['id']}` · ~{n['travel_cooldown_minutes']:.0f}min"
            for n in m["neighbors"]
        ]
        e = simple_result_embed(True, "\n".join(lines) or "You stand at the edge of all things.",
                                title=f"🗺️ {cur['name']} (Danger {cur['danger_tier']}, Qi ×{cur['spirit_density']:.1f})")
        await interaction.followup.send(embed=e)
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="travel", description="Journey to an adjacent node (use /map for ids)")
async def travel(interaction: discord.Interaction, target_node_id: str):
    await interaction.response.defer()
    try:
        r = await api.travel(_user_id(interaction), target_node_id)
        await interaction.followup.send(embed=simple_result_embed(r["success"], r["message"], title="🧭 Travel"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="explore", description="Explore your surroundings")
@app_commands.describe(ambush_choice="Pre-choose what to do if ambushed (default: auto)")
@app_commands.choices(ambush_choice=[
    app_commands.Choice(name="fight", value="fight"),
    app_commands.Choice(name="flee", value="flee"),
])
async def explore(interaction: discord.Interaction, ambush_choice: Optional[str] = None):
    await interaction.response.defer()
    try:
        r = await api.explore(_user_id(interaction), ambush_choice)
        await interaction.followup.send(embed=simple_result_embed(True, r["message"], title=f"🔍 {r['encounter'].replace('_', ' ').title()}"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="merchant", description="The Wandering Merchant's daily stalls")
async def merchant(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        m = await api.merchant(_user_id(interaction))
        lines = [f"**{s['name']}** — {s['price_low_stones']:,} stones · `{s['item_id']}`" for s in m["stalls"]]
        await interaction.followup.send(embed=simple_result_embed(True, "\n".join(lines)[:4000], title="🛒 Merchant Pavilion"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="buy", description="Buy today's merchant special")
async def buy(interaction: discord.Interaction, item_id: str):
    await interaction.response.defer()
    try:
        r = await api.buy(_user_id(interaction), item_id)
        await interaction.followup.send(embed=simple_result_embed(True, r["message"], title="💰 Purchase"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="sell", description="Sell items from your pouch")
async def sell(interaction: discord.Interaction, item_id: str, quantity: int = 1):
    await interaction.response.defer()
    try:
        r = await api.sell(_user_id(interaction), item_id, quantity)
        await interaction.followup.send(embed=simple_result_embed(True, r["message"], title="💰 Sale"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="convert", description="Condense or split spirit stone grades")
@app_commands.choices(direction=[app_commands.Choice(name="up (wallet → higher grade)", value="up"),
                                 app_commands.Choice(name="down (grade → wallet)", value="down")])
async def convert(interaction: discord.Interaction, direction: str, grade: str, amount: int):
    await interaction.response.defer()
    try:
        r = await api.convert(_user_id(interaction), direction, grade, amount)
        await interaction.followup.send(embed=simple_result_embed(True, r["message"], title="💎 Conversion"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="soul-state", description="Inspect your soul (vitality, legacy, lineage)")
async def soul_state_cmd(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        s = await api.soul_state(_user_id(interaction))
        await interaction.followup.send(embed=simple_result_embed(True, s["message"], title=f"👻 Soul: {s['soul_state']}"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="possess", description="[Remnant Souls] Seize a mortal vessel")
async def possess(interaction: discord.Interaction, target_name: str,
                  target_strength: app_commands.Range[float, 1.0, 10.0] = 3.0):
    await interaction.response.defer()
    try:
        s = await api.possess(_user_id(interaction), target_name[:60], target_strength)
        await interaction.followup.send(embed=simple_result_embed(True, s["message"], title="👹 Duo She"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="reincarnate", description="[Dead/Remnant only] Spend karmic legacy on rebirth")
async def reincarnate(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        r = await api.reincarnate(_user_id(interaction))
        e = simple_result_embed(True, r["message"], title=f"☸️ Reborn — Generation {r['lineage_generation']}")
        e.add_field(name="Karmic Blessings", value=f"+{r['root_luck_bonus']:.0%} rare-root luck · +{r['starting_stone_bonus']} stones",
                    inline=False)
        await interaction.followup.send(embed=e)
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))


@bot.tree.command(name="tribulation", description="Face your Heavenly Tribulation")
async def tribulation_cmd(interaction: discord.Interaction):
    await send_tribulation_status(interaction, api, _user_id(interaction))


@bot.tree.command(name="narrate", description="Ask The Heavenly Dao to narrate a moment of your life")
@app_commands.choices(event_type=[
    app_commands.Choice(name="breakthrough", value="breakthrough"),
    app_commands.Choice(name="windfall", value="windfall"),
    app_commands.Choice(name="reincarnation", value="reincarnation"),
])
async def narrate(interaction: discord.Interaction, event_type: str):
    await interaction.response.defer()
    try:
        n = await api.narrate(_user_id(interaction), event_type)
        tag = "" if not n.get("fell_back") else " *(heaven is quiet — fallback voice)*"
        await interaction.followup.send(embed=simple_result_embed(
            True, f"*{n['narration']}*{tag}", title="☁️ The Heavenly Dao"))
    except ApiError as ex:
        await interaction.followup.send(embed=_err_embed(ex))
