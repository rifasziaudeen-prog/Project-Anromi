"use client";

import React, { useState } from "react";
import { useStore } from "@/lib/store";
import { Btn } from "./ui";

export default function EntryGate() {
  const { enter } = useStore();
  const [value, setValue] = useState("");
  const [err, setErr] = useState("");

  const submit = () => {
    const id = value.trim();
    if (!/^\d{5,25}$/.test(id)) {
      setErr("Enter your numeric Discord user ID (enable Developer Mode → right-click your name → Copy ID).");
      return;
    }
    setErr("");
    enter(id);
  };

  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="panel p-8 w-full max-w-md text-center storm-glow">
        <h1 className="font-display text-4xl text-gold tracking-widest mb-1">ANROMI</h1>
        <p className="text-mist text-sm mb-1">逆天改命 · Defy Heaven, Change Fate</p>
        <div className="gold-rule my-4" />
        <p className="text-parchment text-sm mb-5">
          Speak your identity, wanderer, and heaven shall open its ledger.
        </p>
        <input
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="Discord ID (numbers only)"
          inputMode="numeric"
          className="w-full bg-ink-800 border border-gold/30 rounded-lg px-4 py-2.5 text-center
                     text-parchment placeholder:text-mist/50 focus:outline-none focus:border-gold"
        />
        {err && <p className="text-red-400 text-xs mt-2">{err}</p>}
        <Btn tone="gold" className="mt-5 w-full" onClick={submit}>
          Begin Cultivation
        </Btn>
        <p className="text-mist/60 text-[11px] mt-4">
          Prototype identity: your Discord user ID doubles as your account.
        </p>
      </div>
    </div>
  );
}
