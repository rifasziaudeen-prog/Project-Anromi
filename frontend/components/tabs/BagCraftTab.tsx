"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useStore } from "@/lib/store";
import { api, BagEntry, Blueprint, RecipeInfo } from "@/lib/api";
import { Btn, Chip, Empty, Panel } from "../ui";

export default function BagCraftTab() {
  const { did, act } = useStore();
  const [bag, setBag] = useState<{ entries: BagEntry[]; spirit_stones: number; pill_toxicity: number } | null>(null);
  const [recipes, setRecipes] = useState<RecipeInfo[]>([]);
  const [mastery, setMastery] = useState<{ level: number; title: string } | null>(null);
  const [blueprints, setBlueprints] = useState<Blueprint[]>([]);
  const [equipped, setEquipped] = useState<Record<string, string | null>>({});
  const [lastRefine, setLastRefine] = useState<{ grade: string; impurity: number; msg: string } | null>(null);

  const loadAll = useCallback(async () => {
    if (!did) return;
    try {
      const [b, r, bp, prof] = await Promise.all([api.bag(did), api.recipes(did), api.blueprints(), api.profile(did)]);
      setBag(b);
      setRecipes(r.recipes);
      setMastery({ level: r.alchemy_level, title: r.alchemy_title });
      setBlueprints(bp);
      setEquipped({
        weapon: (prof as unknown as Record<string, string>).equipped_weapon ?? null,
        armor: (prof as unknown as Record<string, string>).equipped_armor ?? null,
      });
    } catch {
      /* transient */
    }
  }, [did]);

  useEffect(() => {
    loadAll();
    const t = setInterval(loadAll, 20000);
    return () => clearInterval(t);
  }, [loadAll]);

  if (!bag) return <Panel title="🎒 Pouch"><Empty text="Loading your spatial pouch..." /></Panel>;

  const refine = async (r: RecipeInfo) => {
    await act(() => api.refine(did!, r.id, "furnace_mortal_iron", "flame_wood"));
    loadAll();
  };

  const consumePill = async (e: BagEntry) => {
    await act(() => api.consume(did!, e.item_id, e.quality ?? undefined));
    loadAll();
  };

  const craft = async (bp: Blueprint) => {
    await act(() => api.craft(did!, bp.id));
    loadAll();
  };

  const equipToggle = async (slot: string, itemId: string | null) => {
    await act(() => api.equip(did!, slot, itemId));
    loadAll();
  };

  const pills = bag.entries.filter((e) => e.category === "Pill");
  const mats = bag.entries.filter((e) => e.category !== "Pill" && e.category !== "Currency");
  const currencies = bag.entries.filter((e) => e.category === "Currency");

  return (
    <div className="space-y-4">
      <Panel title={`🎒 Pouch · 💎 ${bag.spirit_stones.toLocaleString()} stones · ☠️ Toxicity ${bag.pill_toxicity.toFixed(0)}`}>
        {pills.length === 0 && mats.length === 0 && <Empty text="Empty. The void stares back." />}
        {pills.length > 0 && (
          <>
            <h3 className="text-xs uppercase text-mist mb-2">Pills</h3>
            <div className="space-y-1.5 mb-4">
              {pills.map((e) => (
                <div key={e.item_id + e.quality} className="flex items-center justify-between bg-ink-800 rounded-lg px-3 py-2">
                  <span className="text-sm">{e.name} <span className="text-gold">[{e.quality}]</span> ×{e.quantity}</span>
                  <Btn tone="soul" onClick={() => consumePill(e)}>Consume</Btn>
                </div>
              ))}
            </div>
          </>
        )}
        {mats.length > 0 && (
          <>
            <h3 className="text-xs uppercase text-mist mb-2">Materials & Gear</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 text-sm">
              {mats.map((e) => (
                <div key={e.item_id} className="bg-ink-800 rounded-lg px-3 py-2 flex justify-between">
                  <span>{e.name}</span><span className="text-mist">×{e.quantity}</span>
                </div>
              ))}
            </div>
          </>
        )}
        {currencies.length > 0 && (
          <div className="mt-3 flex gap-2 flex-wrap">
            {currencies.map((e) => (
              <span key={e.item_id} className="text-xs bg-gold/10 border border-gold/30 text-gold rounded-full px-3 py-1">
                {e.name} ×{e.quantity}
              </span>
            ))}
          </div>
        )}
      </Panel>

      <Panel title={`⚗️ Alchemy ${mastery ? `· Lv${mastery.level} ${mastery.title}` : ""}`}>
        {recipes.length === 0 && <Empty text="No recipes known." />}
        <div className="space-y-2">
          {recipes.map((r) => (
            <div key={r.id} className="bg-ink-800 rounded-lg p-3">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <p className="text-sm font-medium">
                    {r.craftable_now ? "✅" : "🔒"} {r.name}{" "}
                    <span className="text-mist text-xs">T{r.tier} · Lv{r.alchemy_level_req}+ · impurity base {r.base_impurity}%</span>
                  </p>
                  <p className="text-xs text-mist mt-0.5">{r.blurb}</p>
                  <p className="text-[11px] text-mist/70 mt-0.5">
                    {Object.entries(r.materials).map(([k, v]) => `${k.replace(/_/g, " ")} ×${v}`).join(" · ")}
                  </p>
                </div>
                <Btn tone="jade" disabled={!r.craftable_now} onClick={() => refine(r)}>Brew</Btn>
              </div>
            </div>
          ))}
        </div>
      </Panel>

      <Panel title={`🔨 Forging`}>
        <div className="space-y-2">
          {blueprints.map((bp) => {
            const isEq = equipped[bp.slot] === bp.id;
            return (
              <div key={bp.id} className="bg-ink-800 rounded-lg p-3 flex items-center justify-between gap-2">
                <div>
                  <p className="text-sm font-medium">
                    {bp.name} <span className="text-mist text-xs">{bp.slot} · {bp.tier} · Qi +{(bp.passive_qi_bonus * 100).toFixed(0)}% · Lv{bp.forging_level_req}+</span>
                  </p>
                  <p className="text-[11px] text-mist/70">
                    {Object.entries(bp.materials).map(([k, v]) => `${k.replace(/_/g, " ")} ×${v}`).join(" · ")}
                  </p>
                </div>
                <div className="flex gap-1.5 shrink-0">
                  {isEq ? (
                    <Btn tone="ghost" onClick={() => equipToggle(bp.slot, null)}>Unequip</Btn>
                  ) : (
                    <Btn tone="gold" onClick={() => equipToggle(bp.slot, bp.id)}>Equip</Btn>
                  )}
                  <Btn tone="jade" onClick={() => craft(bp)}>Forge</Btn>
                </div>
              </div>
            );
          })}
        </div>
      </Panel>

      {lastRefine && (
        <Panel title="Last Brew">
          <Chip label="Grade" value={lastRefine.grade} tone="gold" />
          <Chip label="Impurity" value={`${lastRefine.impurity}%`} tone={lastRefine.impurity! > 32 ? "blood" : "jade"} />
        </Panel>
      )}
    </div>
  );
}
