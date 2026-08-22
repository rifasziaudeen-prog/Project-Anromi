"""Discord embed builders — presentation only, no game logic."""
import discord
from typing import Dict, Any, Optional

REALM_ICONS = {
    1: "🌱", 2: "🌊", 3: "⭐", 4: "👶", 5: "👁️", 6: "🌌", 7: "🗿", 8: "⚡",
    9: "🗡️", 10: "🥇", 11: "🔮", 12: "🕰️", 13: "📜", 14: "🌀", 15: "🌍", 16: "♾️",
}


def _bar(current: float, maximum: float, length: int = 12) -> str:
    ratio = max(0.0, min(1.0, current / max(1.0, maximum)))
    filled = int(round(ratio * length))
    return "█" * filled + "░" * (length - filled)


def profile_embed(p: Dict[str, Any]) -> discord.Embed:
    icon = REALM_ICONS.get(p.get("realm", 1), "🌱")
    e = discord.Embed(
        title=f"{icon} {p.get('dao_title', 'Cultivator')} {p['username']}",
        description=(
            f"**{p['realm_name_en']}** ({p['realm_name_cn']}) · {p['stage']}\n"
            f"`Qi  {_bar(p['spirit_energy'], p['max_energy'])}` "
            f"{p['spirit_energy']:.0f}/{p['max_energy']:.0f}\n"
            f"Root: **{p['spiritual_root']}** ({p['spiritual_root_purity']:.2f})\n"
            f"Physique: **{p['physique_name']}**"
        ),
        color=discord.Color.purple()
    )
    e.add_field(name="🧘 Dao Heart", value=f"{p['dao_heart_stability']:.0f}/100", inline=True)
    e.add_field(name="☠️ Karma Sin", value=str(p["karma_sin"]), inline=True)
    e.add_field(name="🔥 Streak", value=f"{p['streak_days']}d (best {p['best_streak']})", inline=True)
    e.add_field(name="💊 Toxicity", value=f"{p['pill_toxicity']:.0f}/100", inline=True)
    e.add_field(name="💎 Stones", value=f"{p['spirit_stones']:,}", inline=True)
    e.add_field(name="🏆 Wins/Fails", value=f"{p['total_breakthrough_wins']}/{p['total_breakthrough_fails']}", inline=True)
    if p.get("alchemy_level") is not None:
        e.add_field(name="⚗️ Alchemy", value=f"Lv{p['alchemy_level']} {p.get('alchemy_title') or ''}", inline=True)
        e.add_field(name="🔨 Forging", value=f"Lv{p['forging_level']} {p.get('forging_title') or ''}", inline=True)
        e.add_field(name="🎲 Luck", value=str(p.get("luck_stat", "?")), inline=True)
    if p.get("soul_state") == "REMNANT_SOUL":
        e.set_footer(text=f"👻 REMNANT SOUL — vitality {p['remnant_soul_vitality']:.0f}/100 · Gen {p['lineage_generation']}")
    elif p.get("is_dead"):
        e.set_footer(text=f"☠️ TRULY DEAD · {p['karmic_legacy_tokens']} legacy tokens await rebirth")
    else:
        lifespan = p["lifespan_current_years"]
        e.set_footer(text=f"Age {lifespan:.0f} / {p['lifespan_max_years']:.0f} yrs · Gen {p['lineage_generation']}")
    return e


def tribulation_embed(summary: Dict[str, Any], log_tail: list = None) -> discord.Embed:
    s = summary
    remaining = s["total_strikes"] - s["strikes_endured"]
    e = discord.Embed(
        title=f"☁️ {s['tier'].replace('_', '-')} Tribulation",
        description=(
            f"Crossing into **Realm {s['target_realm']}**\n"
            f"`Strikes {_bar(s['strikes_endured'], s['total_strikes'], 16)}` "
            f"{s['strikes_endured']}/{s['total_strikes']} ({remaining} remain)\n"
            f"`Body  {_bar(s['body_pool'], 100)}` {s['body_pool']:.0f} integrity\n"
            f"`Qi    {_bar(s['qi_pool'], 100)}` {s['qi_pool']:.0f}"
        ),
        color=discord.Color.dark_gold()
    )
    gear = ", ".join(f"{k}: {v}" for k, v in s.get("gear", {}).items() if v) or "bare hands"
    e.add_field(name="🗡️ Gear", value=gear[:200] or "—", inline=False)
    if s.get("shield"):
        e.add_field(name="🛡️ Ward", value=f"{s['shield']:.0f} absorption", inline=True)
    e.add_field(name="🧠 Dao Heart", value=f"{s['dao_heart']:.0f}", inline=True)
    for line in (log_tail or [])[-3:]:
        e.description += f"\n> {line[:120]}"
    return e


def event_embed(ev: Dict[str, Any]) -> discord.Embed:
    etype = ev["event_type"]
    titles = {
        "breakthrough": "✨ Breakthrough!",
        "tribulation_summoned": "☁️ Tribulation Summoned",
        "tribulation_survived": "🌅 Tribulation Survived",
        "tribulation_destroyed": "💀 Body Destroyed by Heaven",
        "true_death": "☠️ True Death",
        "windfall": "🌟 Windfall Epiphany",
        "reincarnation": "☸️ Reincarnation",
        "possession": "👹 Possession",
    }
    payload = ev.get("payload", {})
    desc_bits = []
    for key in ("realm_name_en", "target_realm", "tier", "total_strikes", "strikes_endured",
                "realm_advanced_to", "legacy_awarded", "lineage_generation", "windfall_message",
                "spiritual_root", "physique_name", "target_name", "dao_title"):
        if key in payload and payload[key]:
            label = key.replace("_", " ").title()
            desc_bits.append(f"**{label}:** {payload[key]}")
    color_map = {
        "breakthrough": discord.Color.green(),
        "tribulation_survived": discord.Color.gold(),
        "tribulation_destroyed": discord.Color.red(),
        "true_death": discord.Color.dark_red(),
    }
    e = discord.Embed(
        title=titles.get(etype, f"📣 {etype.replace('_', ' ').title()}"),
        description="\n".join(desc_bits)[:2000],
        color=color_map.get(etype, discord.Color.blurple())
    )
    if ev.get("username"):
        e.set_author(name=ev["username"])
    return e


def simple_result_embed(success: bool, message: str, title: Optional[str] = None) -> discord.Embed:
    return discord.Embed(
        title=title or ("✅ Success" if success else "❌ Failed"),
        description=message[:4000],
        color=discord.Color.green() if success else discord.Color.red()
    )
