"use client";

import React, { useState } from "react";
import { StoreProvider, useStore } from "@/lib/store";
import EntryGate from "@/components/EntryGate";
import ProfileTab from "@/components/tabs/ProfileTab";
import TribulationTab from "@/components/tabs/TribulationTab";
import BagCraftTab from "@/components/tabs/BagCraftTab";
import WorldTab from "@/components/tabs/WorldTab";
import SoulTab from "@/components/tabs/SoulTab";
import ChronicleFeed from "@/components/ChronicleFeed";

const TABS = [
  { id: "profile", label: "🧘 Profile" },
  { id: "tribulation", label: "⛈️ Tribulation" },
  { id: "bag", label: "🎒 Bag & Craft" },
  { id: "world", label: "🗺️ World" },
  { id: "soul", label: "👻 Soul" },
] as const;

type TabId = (typeof TABS)[number]["id"];

function Toasts() {
  const { toasts } = useStore();
  if (toasts.length === 0) return null;
  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2 w-80 max-w-[90vw]">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`panel p-3 text-sm border-l-4 ${
            t.ok ? "border-l-jade text-parchment" : "border-l-blood text-red-200"
          }`}
        >
          {t.text}
        </div>
      ))}
    </div>
  );
}

function Dashboard() {
  const { profile, logout } = useStore();
  const [tab, setTab] = useState<TabId>("profile");

  const tribActive = profile?.soul_state !== undefined && false; // storm state lives in its own tab

  return (
    <div className="flex-1 w-full max-w-6xl mx-auto p-4">
      {/* Header */}
      <header className="flex items-center justify-between mb-4">
        <h1 className="font-display text-xl text-gold tracking-widest">ANROMI <span className="text-mist text-xs normal-case tracking-normal">· 仙途</span></h1>
        <button onClick={logout} className="text-xs text-mist hover:text-parchment">
          leave this body ({profile?.username ?? "..."})
        </button>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-4">
        <div>
          {/* Tab bar */}
          <nav className="flex gap-1.5 mb-4 overflow-x-auto pb-1">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`px-3.5 py-2 rounded-lg text-sm whitespace-nowrap border transition-colors ${
                  tab === t.id
                    ? "bg-gold/15 border-gold text-gold"
                    : "bg-transparent border-ink-700 text-mist hover:text-parchment"
                }`}
              >
                {t.label}
              </button>
            ))}
          </nav>

          {tab === "profile" && <ProfileTab />}
          {tab === "tribulation" && <TribulationTab />}
          {tab === "bag" && <BagCraftTab />}
          {tab === "world" && <WorldTab />}
          {tab === "soul" && <SoulTab />}
        </div>

        {/* Chronicle sidebar */}
        <aside className="hidden lg:block">
          <ChronicleFeed />
        </aside>
      </div>
      <Toasts />
    </div>
  );
}

function Gate() {
  const { did, ready } = useStore();
  if (!ready) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-mist animate-pulse font-display">Opening heaven's ledger...</p>
      </div>
    );
  }
  return did ? <Dashboard /> : <EntryGate />;
}

export default function Home() {
  return (
    <StoreProvider>
      <main className="flex flex-col min-h-screen">
        <Gate />
        <footer className="text-center text-[11px] text-mist/50 py-3">
          ☁️ The Heavenly Dao observes. · Project Anromi v0.6.0
        </footer>
      </main>
    </StoreProvider>
  );
}
