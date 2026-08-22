"""Interactive Discord UI for Heavenly Tribulations — one wave per button."""
import discord
from typing import Dict, Any

from bot.api_client import AnromiClient, ApiError
from bot.embeds import tribulation_embed, simple_result_embed


class TribulationView(discord.ui.View):
    """⚔️ Endure · 🗡️ Sacrifice · 💊 Pill · 🏳️ Bail — one wave resolved per click."""

    def __init__(self, api: AnromiClient, discord_id: str, timeout: float = 600):
        super().__init__(timeout=timeout)
        self.api = api
        self.discord_id = discord_id
        self.busy = False

    async def _resolve(self, interaction: discord.Interaction, action: str):
        if self.busy:
            await interaction.response.defer()
            return
        self.busy = True
        try:
            await interaction.response.defer()
            result = await self.api.tribulation_action(self.discord_id, action)
            outcome = result["outcome"]

            if outcome == "ONGOING":
                embed = tribulation_embed(result["summary"], log_tail=result.get("events", []))
                events = "\n> ".join(result.get("events", [])[-3:])
                if events:
                    embed.add_field(name="This Wave", value=events[:1000], inline=False)
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                finished = simple_result_embed(
                    success=(outcome == "SURVIVED"),
                    message="\n".join(result.get("events", [])[-6:])[:4000],
                    title={
                        "SURVIVED": "🌅 TRIBULATION SURVIVED!",
                        "DESTROYED": "💀 BODY DESTROYED",
                        "BAILED": "🏳️ You Fled the Storm",
                    }.get(outcome, outcome)
                )
                if result.get("realm_advanced_to"):
                    finished.add_field(name="Ascended To", value=f"Realm {result['realm_advanced_to']}", inline=False)
                if result.get("soul_fate"):
                    finished.add_field(name="Soul Fate", value=result["soul_fate"], inline=True)
                destroyed = result.get("destroyed_artifacts") or []
                if destroyed:
                    finished.add_field(name="Artifacts Lost", value=", ".join(destroyed)[:1000], inline=False)
                for child in self.children:
                    child.disabled = True
                await interaction.edit_original_response(embed=finished, view=self)
                self.stop()
        except ApiError as ex:
            await interaction.edit_original_response(
                embed=simple_result_embed(False, str(ex.detail)), view=self
            )
        finally:
            self.busy = False

    @discord.ui.button(label="Endure", emoji="⚔️", style=discord.ButtonStyle.primary)
    async def endure(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._resolve(interaction, "endure")

    @discord.ui.button(label="Pill", emoji="💊", style=discord.ButtonStyle.success)
    async def pill(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._resolve(interaction, "pill")

    @discord.ui.button(label="Sacrifice Sword", emoji="🗡️", style=discord.ButtonStyle.danger)
    async def sacrifice_weapon(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._resolve(interaction, "sacrifice:weapon")

    @discord.ui.button(label="Sacrifice Armor", emoji="🛡️", style=discord.ButtonStyle.danger)
    async def sacrifice_armor(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._resolve(interaction, "sacrifice:armor")

    @discord.ui.button(label="Bail Out", emoji="🏳️", style=discord.ButtonStyle.secondary)
    async def bail(self, interaction: discord.Interaction, _: discord.ui.Button):
        await self._resolve(interaction, "bail")


async def send_tribulation_status(interaction: discord.Interaction, api: AnromiClient,
                                  discord_id: str) -> None:
    state = await api.tribulation_state(discord_id)
    if not state.get("active"):
        await interaction.response.send_message(
            embed=simple_result_embed(False, state.get("message", "No storm gathers above you.")),
            ephemeral=True
        )
        return
    summary = state["summary"]
    # Fresh storms need initiation before wave actions
    if summary.get("waves_remaining") is not None and summary["strikes_endured"] == 0:
        try:
            await api.tribulation_initiate(discord_id)
        except ApiError:
            pass
    embed = tribulation_embed(summary, log_tail=state.get("log_tail", []))
    await interaction.response.send_message(embed=embed, view=TribulationView(api, discord_id))
