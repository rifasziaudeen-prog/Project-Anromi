"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useStore } from "@/lib/store";
import { api, MerchantStall } from "@/lib/api";
import { Btn, Empty, Panel } from "../ui";

export default function WorldTab() {
  const { did, act } = useStore();
  const [map, setMap] = useState<Awaited<ReturnType<typeof api.map>> | null>(null);
  const [stalls, setStalls] = useState<MerchantStall[] | null>(null);
  const [lastExplore, setLastExplore] = useState("");

  const load = useCallback(async () => {
    if (!did) return;
    try {
      const m = await api.map(did);
      setMap(m);
    } catch {
      /* transient */
    }
  }, [did]);

  useEffect(() => {
    load();
    const t = setInterval(load, 20000);
    return () => clearInterval(t);
  }, [load]);

  if (!map) return <Panel title="🗺️ World"><Empty text="Consulting the celestial atlas..." /></Panel>;

  const cur = map.current_node;

  const travel = async (nodeId: string) => {
    const r = await act(() => api.travel(did!, nodeId));
    if (r?.success) load();
  };

  const explore = async () => {
    const r = await act(() => api.explore(did!));
    if (r) {
      setLastExplore(`${r.encounter.replace("_", " ")} — ${r.message}`);
      load();
    }
  };

  const openCaravan = async () => {
    try {
      const m = await api.merchant(did!);
      setStalls(m.stalls);
    } catch {
      /* handled */
    }
  };

  return (
    <div className="space-y-4">
      <Panel title="📍 Current Location">
        <div className="flex items-baseline justify-between">
          <h3 className="font-display text-lg text-gold">{cur.name}</h3>
          <span className="text-xs text-blood">Danger {cur.danger_tier}</span>
        </div>
        <p className="text-xs text-mist mt-1">{cur.region} · {cur.plane} · Qi density ×{cur.spirit_density.toFixed(1)} · Bias: {cur.elemental_bias}</p>
        <p className="text-sm text-parchment/80 italic mt-2">{cur.description}</p>
        <Btn tone="jade" className="mt-4" onClick={explore}>🔍 Explore</Btn>
        {lastExplore && <p className="text-sm text-parchment/90 mt-3 bg-ink-800 rounded-lg p-3">{lastExplore}</p>}
      </Panel>

      <Panel title="🧭 Paths From Here">
        {map.neighbors.length === 0 && <Empty text="You stand at the edge of the known world." />}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {map.neighbors.map((n) => (
            <div key={n.id} className="bg-ink-800 rounded-lg p-3 flex items-center justify-between gap-2">
              <div>
                <p className="text-sm font-medium">{n.name}</p>
                <p className="text-[11px] text-mist">{n.region} · Danger {n.danger_tier} · ~{n.travel_cooldown_minutes.toFixed(0)}min · -{(n.qi_cost_pct * 100).toFixed(0)}% Qi</p>
              </div>
              <Btn tone="gold" onClick={() => travel(n.id)}>Travel</Btn>
            </div>
          ))}
        </div>
      </Panel>

      {stalls && stalls.length > 0 && (
        <Panel title="🛒 Wandering Caravan (today only)">
          <div className="space-y-1.5">
            {stalls.map((s) => (
              <div key={s.item_id} className="flex items-center justify-between bg-ink-800 rounded-lg px-3 py-2">
                <span className="text-sm">{s.name} <span className="text-mist text-xs">`{s.item_id}`</span></span>
                <Btn tone="gold" onClick={() => act(() => api.buy(did!, s.item_id))}>
                  💎 {s.price_low_stones.toLocaleString()}
                </Btn>
              </div>
            ))}
          </div>
        </Panel>
      )}
      {!stalls && (
        <Btn tone="ghost" onClick={openCaravan}>Check for a wandering caravan...</Btn>
      )}
    </div>
  );
}
