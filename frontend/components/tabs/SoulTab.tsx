"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useStore } from "@/lib/store";
import { api } from "@/lib/api";
import { Btn, Chip, Empty, Panel } from "../ui";

export default function SoulTab() {
  const { did, act, profile, refreshProfile } = useStore();
  const [soul, setSoul] = useState<Awaited<ReturnType<typeof api.soulState>> | null>(null);
  const [vesselName, setVesselName] = useState("");
  const [strength, setStrength] = useState(3);

  const load = useCallback(async () => {
    if (!did) return;
    try {
      setSoul(await api.soulState(did));
    } catch {
      /* transient */
    }
  }, [did]);

  useEffect(() => {
    load();
    if (profile?.is_remnant_soul) {
      // vitality decays in real time — poll faster while bodiless
      const t = setInterval(load, 10000);
      return () => clearInterval(t);
    }
  }, [load, profile?.is_remnant_soul]);

  if (!soul) return <Panel title="👻 Soul"><Empty text="Peering into the soul..." /></Panel>;

  const possess = async () => {
    await act(() => api.possess(did!, vesselName || "Nameless Mortal", strength));
    await refreshProfile();
    load();
  };

  const reincarnate = async () => {
    await act(() => api.reincarnate(did!));
    await refreshProfile();
    load();
  };

  const isRemnant = soul.soul_state === "REMNANT_SOUL";
  const isDead = soul.soul_state === "DEAD";

  return (
    <div className="space-y-4">
      <Panel title="👻 Soul State">
        <Chip label="State" value={soul.soul_state.replace("_", " ")} tone={isDead ? "blood" : isRemnant ? "soul" : "jade"} />
        <Chip label="Deaths" value={soul.death_count} />
        <Chip label="Lineage Generation" value={`Gen ${soul.lineage_generation}`} />
        <Chip label="Karmic Legacy Tokens" value={`☸️ ${soul.karmic_legacy_tokens}`} tone="gold" />
        {isRemnant && (
          <>
            <div className="mt-3">
              <Chip label="Soul Vitality" value={`${soul.remnant_soul_vitality.toFixed(1)} / 100`} tone="blood" />
              <p className="text-xs text-mist mt-2">
                ⏳ ~{((soul.remnant_soul_vitality / 4)).toFixed(1)}h before your soul-fire extinguishes. Find a vessel or rebirth.
              </p>
            </div>
            <div className="mt-4 space-y-2">
              <input
                value={vesselName}
                onChange={(e) => setVesselName(e.target.value)}
                placeholder="Vessel's name (a mortal nearby...)"
                className="w-full bg-ink-800 border border-soul/30 rounded-lg px-3 py-2 text-sm text-parchment
                           placeholder:text-mist/50 focus:outline-none focus:border-soul"
              />
              <label className="text-xs text-mist flex items-center gap-3">
                Vessel strength: {strength.toFixed(0)}/10
                <input type="range" min={1} max={10} step={1} value={strength}
                       onChange={(e) => setStrength(Number(e.target.value))} className="flex-1 accent-[#9b7ede]" />
              </label>
              <Btn tone="soul" className="w-full" onClick={possess}>👹 Attempt Possession</Btn>
            </div>
          </>
        )}
        {(isDead || isRemnant) && (
          <div className="mt-4">
            <Btn tone="gold" className="w-full" onClick={reincarnate}>
              ☸️ Reincarnate ({soul.karmic_legacy_tokens} legacy tokens → blessings)
            </Btn>
            <p className="text-[11px] text-mist mt-2 text-center">
              Spends ALL legacy tokens on rare-root luck and starting wealth for your next life.
            </p>
          </div>
        )}
        {!isDead && !isRemnant && (
          <Empty text="Your soul rests safely within its flesh. Cultivate — death comes for the careless." />
        )}
      </Panel>
    </div>
  );
}
