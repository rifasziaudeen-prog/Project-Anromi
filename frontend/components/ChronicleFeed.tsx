"use client";

import React, { useCallback, useEffect, useState } from "react";
import { api, EventItem } from "@/lib/api";
import { Panel } from "./ui";

const EVENT_ICONS: Record<string, string> = {
  breakthrough: "✨",
  tribulation_summoned: "☁️",
  tribulation_survived: "🌅",
  tribulation_destroyed: "💀",
  true_death: "☠️",
  windfall: "🌟",
  reincarnation: "☸️",
  possession: "👹",
};

const EVENT_LABELS: Record<string, string> = {
  breakthrough: "Breakthrough",
  tribulation_summoned: "Tribulation Summoned",
  tribulation_survived: "Tribulation Survived",
  tribulation_destroyed: "Body Destroyed",
  true_death: "True Death",
  windfall: "Windfall",
  reincarnation: "Reincarnation",
  possession: "Possession",
};

export default function ChronicleFeed() {
  const [events, setEvents] = useState<EventItem[]>([]);
  const [lastId, setLastId] = useState(0);
  const [narrationProviders, setNarrationProviders] = useState<string>("");

  const poll = useCallback(async () => {
    try {
      const data = await api.events(lastId);
      if (data.events.length > 0) {
        setEvents((prev) => [...data.events.reverse(), ...prev].slice(0, 40));
        setLastId(data.last_id);
      }
    } catch {
      /* API offline — keep showing what we have */
    }
  }, [lastId]);

  useEffect(() => {
    api
      .narrationStatus()
      .then((s) => setNarrationProviders(s.configured_providers.join(", ") || "fallback voice"))
      .catch(() => setNarrationProviders("offline"));
  }, []);

  useEffect(() => {
    poll();
    const t = setInterval(poll, 20000);
    return () => clearInterval(t);
  }, [poll]);

  return (
    <Panel title={`📜 World Chronicle · ☁️ ${narrationProviders}`}>
      {events.length === 0 && (
        <p className="text-mist text-sm italic py-3 text-center">
          The chronicle awaits its first legend...
        </p>
      )}
      <ul className="space-y-2.5 max-h-[60vh] overflow-y-auto pr-1">
        {events.map((ev) => (
          <li key={ev.id} className="text-sm border-l-2 border-gold/30 pl-3 py-0.5">
            <span className="mr-1.5">{EVENT_ICONS[ev.event_type] ?? "📣"}</span>
            <span className="text-gold text-xs uppercase tracking-wide">
              {EVENT_LABELS[ev.event_type] ?? ev.event_type}
            </span>
            {ev.username && <span className="text-parchment"> — {ev.username}</span>}
            <div className="text-mist text-xs mt-0.5">
              {Object.entries(ev.payload)
                .filter(([, v]) => v !== null && v !== undefined)
                .slice(0, 4)
                .map(([k, v]) => (
                  <span key={k} className="mr-2">
                    {k.replace(/_/g, " ")}: <span className="text-parchment/80">{String(v)}</span>
                  </span>
                ))}
            </div>
          </li>
        ))}
      </ul>
    </Panel>
  );
}
