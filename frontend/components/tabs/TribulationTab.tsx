"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useStore } from "@/lib/store";
import { api, TribActionResult } from "@/lib/api";
import { Bar, Btn, Empty, Panel } from "../ui";

export default function TribulationTab() {
  const { did, act } = useStore();
  const [state, setState] = useState<Awaited<ReturnType<typeof api.tribulationState>> | null>(null);
  const [events, setEvents] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  const poll = useCallback(async () => {
    if (!did) return;
    try {
      setState(await api.tribulationState(did));
    } catch {
      /* transient */
    }
  }, [did]);

  useEffect(() => {
    poll();
    const t = setInterval(poll, 5000);
    return () => clearInterval(t);
  }, [poll]);

  const doAction = async (action: string) => {
    setBusy(true);
    try {
      const r: TribActionResult = await api.tribulationAction(did!, action);
      if (r.outcome === "INVALID") {
        act(async () => { throw new Error(r.events[0]); });
      } else {
        if (r.summary) setState({ active: r.outcome === "ONGOING", summary: r.summary, log_tail: [], message: "" });
        else await poll();
        if (r.outcome !== "ONGOING") setEvents(r.events);
        else setEvents((prev) => [...r.events.slice(-2), ...prev].slice(0, 6));
        window.dispatchEvent(
          new CustomEvent("anromi-toast", {
            detail: { msg: r.events[r.events.length - 1] ?? r.outcome, ok: r.outcome !== "DESTROYED" },
          })
        );
      }
    } catch (ex) {
      window.dispatchEvent(new CustomEvent("anromi-toast", {
        detail: { msg: ex instanceof Error ? ex.message : "Heaven erred.", ok: false },
      }));
    } finally {
      setBusy(false);
    }
  };

  if (!state?.active || !state.summary) {
    return (
      <Panel title="⛈️ Heavenly Tribulation">
        <Empty text="No storm gathers above you. Attempt a major realm breakthrough (Realm 4+) and heaven will answer." />
        <p className="text-xs text-mist/70 text-center">
          Prepare well: fill your Qi (it becomes your shield), equip artifacts, and brew Tribulation Shield Pills.
        </p>
      </Panel>
    );
  }

  const s = state.summary;
  const gearEntries = Object.entries(s.gear).filter(([, v]) => v);

  return (
    <div className="space-y-4">
      <Panel className="storm-glow">
        <div className="flex items-baseline justify-between mb-2">
          <h2 className="font-display text-xl text-gold">
            ☁️ {s.tier.replace("_", "-")} Tribulation
          </h2>
          <span className="text-sm text-blood">Crossing → Realm {s.target_realm}</span>
        </div>

        {/* Strike progress */}
        <div className="mb-1 flex justify-between text-xs text-mist">
          <span>Strikes endured</span>
          <span>{s.strikes_endured} / {s.total_strikes}</span>
        </div>
        <div className="h-3 rounded-full bg-ink-700 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-gold-dim to-blood transition-all"
            style={{ width: `${(s.strikes_endured / s.total_strikes) * 100}%` }}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 mt-4">
          <Bar label="Qi Pool" value={s.qi_pool} max={Math.max(s.qi_pool + s.body_pool, 1)} tone="jade" suffix="" />
          <Bar label="Body Integrity" value={s.body_pool} max={Math.max(s.body_pool + s.qi_pool, 1)} tone="gold" suffix="" />
          <Bar label="Dao Heart" value={s.dao_heart} max={100} tone="soul" />
          <Bar label="Shield Ward" value={s.shield} max={Math.max(s.shield, 60)} tone="jade" suffix="" />
        </div>

        {gearEntries.length > 0 && (
          <p className="text-xs text-mist mt-3">🗡️ {gearEntries.map(([k, v]) => `${v}`).join(" · ")}</p>
        )}
        {state.log_tail.length > 0 && (
          <div className="mt-3 space-y-1 max-h-32 overflow-y-auto">
            {state.log_tail.slice(-4).map((line, i) => (
              <p key={i} className="text-xs text-parchment/80">&gt; {line}</p>
            ))}
          </div>
        )}

        <div className="flex flex-wrap gap-2 mt-5">
          <Btn tone="jade" disabled={busy} onClick={() => doAction("endure")}>⚔️ Endure the Wave</Btn>
          <Btn tone="soul" disabled={busy} onClick={() => doAction("pill")}>💊 Shield Pill</Btn>
          <Btn tone="blood" disabled={busy || !s.gear.weapon} onClick={() => doAction("sacrifice:weapon")}
               title="Destroy your sword — nullifies this entire wave">
            🗡️ Sacrifice Sword
          </Btn>
          <Btn tone="blood" disabled={busy || !s.gear.armor} onClick={() => doAction("sacrifice:armor")}
               title="Destroy your armor — nullifies this entire wave">
            🛡️ Sacrifice Armor
          </Btn>
          <Btn tone="ghost" disabled={busy} onClick={() => doAction("bail")}>🏳️ Bail Out</Btn>
        </div>
      </Panel>

      {events.length > 0 && (
        <Panel title="Storm Chronicle">
          <ul className="space-y-1.5 text-sm text-parchment/90">
            {events.map((e, i) => (
              <li key={i}>&gt; {e}</li>
            ))}
          </ul>
        </Panel>
      )}
    </div>
  );
}
