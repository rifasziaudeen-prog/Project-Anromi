"use client";

import React, { useEffect, useState } from "react";
import { useStore } from "@/lib/store";
import { api, Odds } from "@/lib/api";
import { Bar, Btn, Chip, Panel } from "../ui";

const REALM_ICONS: Record<number, string> = {
  1: "🌱", 2: "🌊", 3: "⭐", 4: "👶", 5: "👁️", 6: "🌌", 7: "🗿", 8: "⚡",
  9: "🗡️", 10: "🥇", 11: "🔮", 12: "🕰️", 13: "📜", 14: "🌀", 15: "🌍", 16: "♾️",
};

export default function ProfileTab() {
  const { did, profile, act, refreshProfile } = useStore();
  const [odds, setOdds] = useState<Odds | null>(null);
  const [busy, setBusy] = useState(false);

  const loadOdds = async () => {
    if (!did) return;
    try {
      setOdds(await api.odds(did));
    } catch {
      /* odds are cosmetic here */
    }
  };

  useEffect(() => {
    loadOdds();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [did, profile?.spirit_energy]);

  if (!profile) return null;
  const icon = REALM_ICONS[profile.realm] ?? "🌱";

  const meditate = () =>
    act(() => api.meditate(did!)).then((r) => {
      if (r?.windfall && r.windfall.message) {
        setTimeout(() => alert(`🌟 WINDFALL!\n\n${r.windfall!.message}`), 150);
      }
      loadOdds();
    });

  const breakthrough = async () => {
    setBusy(true);
    try {
      const r = await api.breakthrough(did!);
      if (r.outcome === "TRIBULATION_REQUIRED") {
        alert(r.message); // the Tribulation tab owns the storm from here
      }
      pushResult(r.message, r.success || r.outcome === "TRIBULATION_REQUIRED");
      await refreshProfile();
      loadOdds();
    } catch (ex) {
      pushResult(ex instanceof Error ? ex.message : "Heaven erred.", false);
    } finally {
      setBusy(false);
    }
  };

  const pushResult = (msg: string, ok: boolean) => {
    // reuse the global toast via a custom event so we do not need the hook twice
    window.dispatchEvent(new CustomEvent("anromi-toast", { detail: { msg, ok } }));
  };

  return (
    <div className="space-y-4">
      {/* Realm banner */}
      <Panel>
        <div className="flex items-center gap-4">
          <span className="text-5xl select-none">{icon}</span>
          <div className="flex-1">
            <h1 className="font-display text-2xl text-gold">
              {profile.username} <span className="text-parchment/70 text-base">· {profile.dao_title}</span>
            </h1>
            <p className="text-sm text-mist">
              {profile.realm_name_en} <span className="text-gold-dim">{profile.realm_name_cn}</span> · {profile.stage}
              {profile.is_bottleneck && <span className="text-gold"> · ⚡ Bottleneck reached</span>}
              {profile.stored_breakthrough_bonus > 0 && (
                <span className="text-jade"> · 💊 Pill insight +{Math.round(profile.stored_breakthrough_bonus * 100)}%</span>
              )}
            </p>
          </div>
          <div className="text-right hidden sm:block">
            <p className="text-xs text-mist">Gen {profile.lineage_generation}</p>
            <p className="text-xs text-mist">Age {Math.round(profile.lifespan_current_years)}/{Math.round(profile.lifespan_max_years)} yrs</p>
          </div>
        </div>

        <div className="mt-4 space-y-2.5">
          <Bar label="Spiritual Qi" value={profile.spirit_energy} max={profile.max_energy} tone="jade" />
          {profile.meridian_damage > 0 && (
            <Bar label="Meridian Damage" value={profile.meridian_damage} max={1} tone="blood" />
          )}
        </div>

        <div className="flex flex-wrap gap-2 mt-4">
          <Btn tone="jade" onClick={meditate} disabled={busy}>🧘 Meditate</Btn>
          <Btn
            tone="gold"
            onClick={breakthrough}
            disabled={busy || !odds?.can_attempt}
            title={odds?.can_attempt ? `${(odds.final_chance * 100).toFixed(0)}% chance` : odds?.reason}
          >
            ⚡ Break Through {odds?.can_attempt && `(${(odds.final_chance * 100).toFixed(0)}%)`}
          </Btn>
          {odds?.is_realm_leap && profile.realm >= 3 && (
            <span className="self-center text-xs text-blood animate-pulse">
              Major leap — heaven may demand a tribulation...
            </span>
          )}
        </div>
      </Panel>

      {/* Meters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Panel title="Inner State">
          <Chip label="Dao Heart" value={`${profile.dao_heart_stability.toFixed(0)}/100`} tone={profile.dao_heart_stability < 30 ? "blood" : "jade"} />
          <Chip label="Karma Sin" value={profile.karma_sin} tone={profile.karma_sin >= 300 ? "blood" : "mist"} />
          <Chip label="Pill Toxicity" value={`${profile.pill_toxicity.toFixed(0)}/100`} tone={profile.pill_toxicity >= 50 ? "blood" : "mist"} />
          <Chip label="Qi Purity" value={`${(profile.qi_purity * 100).toFixed(0)}%`} />
        </Panel>
        <Panel title="Path & Fortune">
          <Chip label="Root" value={`${profile.spiritual_root} (${(profile.spiritual_root_purity * 100).toFixed(0)}%)`} tone="gold" />
          <Chip label="Physique" value={profile.physique_name} tone="gold" />
          <Chip label="Luck" value={`🎲 ${profile.luck_stat}`} />
          <Chip label="Streak" value={`🔥 ${profile.streak_days}d (best ${profile.best_streak})`} />
          <Chip label="Dao Insight" value={`💫 ${profile.dao_insight}`} tone="soul" />
        </Panel>
        <Panel title="Craft Mastery">
          <Chip label="Alchemy" value={`Lv${profile.alchemy_level} ${profile.alchemy_title ?? ""}`} tone="soul" />
          <Chip label="Forging" value={`Lv${profile.forging_level} ${profile.forging_title ?? ""}`} tone="soul" />
          <Chip label="Breakthroughs" value={`${profile.total_breakthrough_wins}W / ${profile.total_breakthrough_fails}L`} />
          <Chip label="Highest Realm" value={REALM_ICONS[profile.highest_realm_achieved] + ` R${profile.highest_realm_achieved}`} />
        </Panel>
        <Panel title="Ledger">
          <Chip label="Spirit Stones" value={`💎 ${profile.spirit_stones.toLocaleString()}`} tone="gold" />
          <Chip label="Deaths" value={`☠️ ${profile.death_count}`} />
          <Chip label="Karmic Legacy" value={`☸️ ${profile.karmic_legacy_tokens}`} tone="soul" />
        </Panel>
      </div>
    </div>
  );
}
