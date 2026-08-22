# PROJECT ANROMI — MASTER CONTEXT & MULTI-AGENT FRAMEWORK
**Project Version:** `0.1.0-alpha.1`  
**Last Updated:** 2026-08-16  
**Primary Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy (SQLite Prototype -> MongoDB Migration Target), Pydantic v2.

---

## 🧭 Multi-Agent Collaboration Protocol
This repository is worked on by multiple AI agents (Google Antigravity, Z.ai GLM 5.2, Anthropic Claude, OpenAI models, etc.). **Every AI agent entering this workspace must strictly follow this protocol:**

### ⚡ Entry Checklist for Incoming AI:
1. **Read this file (`CONTEXT.md`) first** to understand the current phase, architectural boundaries, and active session state.
2. **Review the Roadmap Maps** in `docs/roadmap/` (`v0.1.0_core_engine.md` -> `v0.4.0_tribulations_open_world.md`) to verify what is currently in scope vs planned for future phases.
3. **Inspect the Session Ledger** below to check what the previous AI finished and what next handoff goal was assigned.

### 📝 Exit Checklist for Departing AI:
1. **Never break backward compatibility** with established schemas without documenting it.
2. **Update the AI Session Ledger** (increment Session #, log date, model name, summary of edits, and exact next steps for the next AI).
3. **Update the Changelog & Roadmap Checkboxes** to reflect newly implemented features.

---

## 👥 AI Session Ledger & Handoff Tracker

| Session # | Date (UTC) | AI Model | Task / Objective | Key Files Modified | Next Handoff Goal |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `000` | 2026-08-16 | System / Antigravity | Master context & roadmap setup; multi-agent protocol; 16-realm canonical blueprint | `CONTEXT.md`, `docs/roadmap/*` | Begin v0.1.0 Core Engine overhaul. |
| `001` | 2026-08-16 | Antigravity | Core Engine v0.1.0 implementation: 16 Realms (Realms 1-8: 9 Layers + Great Circle; Realms 9-15: Early/Mid/Late/Peak; Realm 16: Supreme). Deep cultivation math engine, meridian capacity, bottlenecks, Pydantic schemas, and API endpoints. | `models/realm.py`, `models/user.py`, `services/cultivation_engine.py`, `schemas/cultivator.py`, `api/routes_cultivator.py`, `main.py` | Implement v0.2.0: 5-Element & Mutant Roots, Physiques, and Remnant Soul Permadeath mechanics. |
| `002` | 2026-08-21 | ox-alpha | v0.2.0 complete: `core/balance.py` master tuning file (all game numbers data-driven), root gacha + physiques (`root_engine.py`), Dao Heart/Karma + Qi Deviation, Remnant Soul permadeath engine (`soul_engine.py`: true death/legacy tokens, possession, reincarnation w/ lineage generations), engagement psychology layer (`engagement_engine.py`: streaks, near-miss, windfalls, titles), generic DB auto-migrator (`core/migrations.py`), soul APIs, 27 passing tests + E2E smoke of full death loop. | `core/balance.py`, `core/migrations.py`, `services/root_engine.py`, `services/soul_engine.py`, `services/engagement_engine.py`, `services/cultivation_engine.py`, `models/user.py`, `schemas/cultivator.py`, `api/routes_cultivator.py`, `api/routes_soul.py`, `main.py`, `tests/test_v2_systems.py`, `task-state.md` | Implement v0.3.0: Alchemy (Dan Dao) with pill toxicity, Forging (Qi Dao), and spirit stone economy. See `task-state.md`. |
| `003` | 2026-08-22 | ox-alpha | v0.3.0 complete: impurity-driven pill grading (mastery lowers center + narrows spread; luck only fires heavenly coincidences; Flawless = zero toxicity — user's core design), alchemy engine w/ furnaces/flames/mastery titles, Pill Toxicity (*Dan Du*) stalling absorption & breakthroughs, booster-pill stored buffs, forging engine (tier-scaled success, material loss on fail) + 4 equip slots feeding meditation bonuses, spirit-stone economy (100:1 grades, auto-breakdown payment, daily UTC-seeded merchant FOMO rotation), placeholder gather endpoint, `inventory_entries` stacks model + NULL-safe stack helpers, 51 passing tests + full E2E smoke (gather→refine→consume→buffed breakthrough→craft/equip→merchant/conversions). | `core/balance.py`, `models/inventory.py`, `models/user.py`, `services/inventory_service.py`, `services/alchemy_engine.py`, `services/forging_engine.py`, `services/economy_engine.py`, `services/gathering_engine.py`, `services/cultivation_engine.py`, `services/engagement_engine.py`, `schemas/inventory.py`, `schemas/cultivator.py`, `api/routes_inventory.py`, `api/routes_alchemy.py`, `api/routes_forging.py`, `api/routes_economy.py`, `api/routes_world.py`, `main.py`, `tests/test_v3_systems.py`, `task-state.md` | Implement v0.4.0: Heavenly Tribulations (multi-wave lightning, artifact sacrifice, permadeath hook) and the open-world node graph engine. See `task-state.md`. |
| `004` | 2026-08-22 | ox-alpha | v0.4.0 complete — FULL ENGINE ROADMAP DONE: mandatory Heavenly Tribulations gating major leaps into Realm 4+ (`TRIBULATION_REQUIRED` state on User.active_tribulation JSON), interactive wave-by-wave resolution (endure/sacrifice-artifact/shield-pill/bail), roadmap damage formula w/ pools model (Qi→body→meridian scars), heart-demon willpower finale vs karma, permadeath hook (Remnant Soul always escapes tribulation; near-miss tragedy messaging), tribulation shield pill recipe; open-world 14-node graph seeded idempotently from balance.WORLD_NODES into world_nodes table, travel w/ Qi cost + danger-scaled lockouts, exploration encounters (danger-scaled herb/mineral age tiers, caravan merchant access, cave gambles, non-lethal ambush clashes), 73 passing tests + E2E smoke (survive 54-strike Six-Nine → Nascent Soul Monarch; unprepared → destroyed → Remnant Soul). | `core/balance.py`, `core/migrations.py`, `models/world.py`, `models/user.py`, `services/tribulation_engine.py`, `services/world_engine.py`, `schemas/world.py`, `api/routes_tribulation.py`, `api/routes_world.py`, `api/routes_cultivator.py`, `main.py`, `tests/test_v4_systems.py`, `task-state.md` | Engine roadmap complete. Next: user decides Direction A (combat engine + sects) vs Direction B (Discord bot / Next.js frontend / Ciel AI narration). See `task-state.md`. |
| `005` | 2026-08-22 | ox-alpha | v0.5.0 complete — Direction B part 1: "The Heavenly Dao" narration engine (`services/narration_service.py`: multi-provider OpenAI-compat fallback chain Groq→Gemini→OpenRouter from .env NARRATION_PROVIDERS, 2026-verified model IDs incl. gemini-3.7-flash & openai/gpt-oss-120b, persona+templates+canned fallbacks in balance.NARRATION, failure logging), GameEvent chronicle (`models/events.py` + hooks in 8 major-moment routes + since_id poll feed), narration APIs (`/api/narration/status|narrate|events/recent`), full Discord bot (`bot/` package: aiohttp api_client, rich embeds, interactive tribulation button view, ~23 slash commands, background server announcer) + run_bot.py entrypoint, .gitignore added. NOTE: user's GEMINI_API_KEY in .env is INVALID (`API_KEY_INVALID`) — regenerate at aistudio.google.com/apikey; fallback lines keep game playable meanwhile. 81 passing tests + smoke (narrate fallback live-proven, chronicle feed, bot imports). | `core/config.py`, `.env.example`, `.gitignore`, `core/balance.py`, `models/events.py`, `services/narration_service.py`, `services/event_service.py`, `api/routes_narration.py`, `api/routes_cultivator.py`, `api/routes_tribulation.py`, `api/routes_soul.py`, `bot/*` (config/api_client/embeds/views/main/__init__), `run_bot.py`, `requirements.txt`, `main.py`, `tests/test_v5_systems.py`, `docs/roadmap/v0.5.0_narration_discord_bot.md` | v0.6.0: Next.js frontend dashboard (dark xianxia theme, profile/actions/bag/world/tribulation screens, Capacitor-ready). See `task-state.md`. |
| `006` | 2026-08-22 | ox-alpha | v0.6.0 complete — Direction B DONE: Next.js 16.3.2 frontend (`frontend/`, App Router+TS+Tailwind v4): single-page tabbed dashboard (Profile w/ meditate+breakthrough+odds, interactive Tribulation storm panel w/ wave actions & pool bars, Bag&Craft w/ recipes/refine/forge/equip, World map/travel/explore/caravan, Soul possession/reincarnation) + Chronicle sidebar polling narration events; typed API layer (`lib/api.ts`) mirroring bot client; global store (`lib/store.tsx`: localStorage identity gate, profile auto-poll, toast system); theme = single Tailwind v4 @theme token block in globals.css; Capacitor-ready. LIVE narration verified through Groq openai/gpt-oss-120b ("The Heavenly Dao speaks"). Root-caused Gemini key failures: OS env var shadowed .env (fixed via load_dotenv override=True + Settings extra=ignore); per-provider multi-MODEL fallback chains added (GROQ_MODELS/GEMINI_MODELS lists); AQ.-prefix OAuth-token detection hint. npm 11 EALLOWSCRIPTS workaround documented. Build clean + E2E verified (API 200, frontend 200). 82 passing tests. | `frontend/*` (package.json, configs, app/layout|page|globals.css, lib/api.ts|store.tsx, components/ui|EntryGate|ChronicleFeed|tabs/*, README.md, .env.local), `core/config.py` (override+extra=ignore, GROQ_MODELS/GEMINI_MODELS), `.env.example`, `services/narration_service.py` (model-chain expansion + AQ. hint), `tests/test_v5_systems.py`, `task-state.md` | User decides: A) Combat engine + Sects, B) Production hardening (Discord OAuth / MongoDB / hosting), or C) Balance playtest pass. See `task-state.md`. |
| `007` | 2026-08-22 | Antigravity | Supabase PostgreSQL Production Migration & Git Multi-Branch Setup: Connected Supabase project (`studisrrfhpesgbxgael`), updated `core/database.py` and `core/migrations.py` for PostgreSQL + SQLite asyncpg dual-compatibility (dynamic connect_args, ANSI TRUE/FALSE booleans), executed live schema creation + world nodes seeding in Supabase Postgres. Created new GitHub repo `rifasziaudeen-prog/Project-Anromi` with branches `main`, `bot-standalone`, `frontend-standalone`, and `backend-api`. Fixed `.env` DATABASE_URL format (pooler hostname + asyncpg driver). | `core/database.py`, `core/migrations.py`, `CONTEXT.md`, `.gitignore` | Proceed with cloud hosting / deployment (Koyeb / Cloudflare Pages / Supabase) or v0.7.0 Combat Engine. |

---

## 🌌 Core Game Vision: Open-World Xianxia Text RPG

Project Anromi is an **open-world, deeply canonical Xianxia text RPG**. Unlike shallow incremental clickers, Anromi features:
1. **Hardcore Permadeath & Remnant Soul Mechanics:** Death is permanent unless the cultivator has forged a Nascent Soul or higher, allowing a desperate race as a **Remnant Soul** (*Canhun*) to possess a mortal vessel, forge a puppet body, or reincarnate with karmic legacy points.
2. **16 Expansive Cultivation Realms:**
   - **Realms 1–8 (Mortal & Earth Steps):** 9 Layers + Great Circle Bottleneck.
   - **Realms 9–15 (Heaven & Immortal Steps):** 4 Sub-stages `[Early, Middle, Late, Peak / Great Perfection]`.
   - **Realm 16 (Cosmic Transcendent):** Absolute Supreme Perfection.
3. **Dynamic Open-World Graph:** A vast living world of continents, mortal empires, hidden sects, spirit veins (*Lingmai*), forbidden abyss zones, dynamic seasonal auctions, and wandering ancient masters.
4. **Deep Systems Ecology:** 5-Element spiritual roots & mutant variants, body constitutions, Dan Dao (alchemy purity & pill toxicity), Qi Dao (forging), and lethal multi-wave Heavenly Tribulations.

---

## 👑 The 16 Grand Realms of Cultivation

```
[MORTAL / HUMAN & EARTH STEP: 9 Layers + Great Circle]
  1. Qi Condensation (炼气)        -> Layer 1 to 9 + Great Circle
  2. Foundation Establishment (筑基) -> Layer 1 to 9 + Great Circle
  3. Golden Core (金丹)             -> Layer 1 to 9 + Great Circle (Grade 1st to 9th Core)
  4. Nascent Soul (元婴)            -> Layer 1 to 9 + Great Circle (★ Remnant Soul survival unlocks!)
  5. Deity Transformation (化神)    -> Layer 1 to 9 + Great Circle (Domain awakening)
  6. Void Refinement (炼虚)         -> Layer 1 to 9 + Great Circle (Dao Severing)
  7. Body Integration (合体)        -> Layer 1 to 9 + Great Circle (Flesh, Soul & Law unity)
  8. Mahayana / Tribulation (大乘)   -> Layer 1 to 9 + Great Circle (Ascension Calamity)

[HEAVEN & IMMORTAL STEP: 4 Sub-stages (Early, Middle, Late, Peak)]
  9. True Immortal (真仙)           -> Early, Middle, Late, Great Perfection (Dao Fruit condensed)
  10. Golden Immortal (金仙)        -> Early, Middle, Late, Great Perfection (Indestructible Golden Body)
  11. Taiyi Golden Immortal (太乙金仙)-> Early, Middle, Late, Great Perfection (Mastery of World Laws)
  12. Daluo Golden Immortal (大罗金仙)-> Early, Middle, Late, Great Perfection (Transcending Spacetime)
  13. Quasi-Saint / Dao Ancestor (准圣)-> Early, Middle, Late, Great Perfection (Dao Incarnations)
  14. Chaos Saint (混元圣人)        -> Early, Middle, Late, Great Perfection (Immortal with the Cosmos)
  15. Sovereign / Creation God (道境) -> Early, Middle, Late, Great Perfection (Universe Genesis)

[COSMIC / SUPREME STEP]
  16. Eternal Transcendent (超脱)   -> Absolute Supreme Perfection (Beyond Heaven and Earth)
```

---

## 📁 Repository Directory Structure

```
Project Anromi/
├── CONTEXT.md                    # Master context & AI session handoff ledger (THIS FILE)
├── PROJECT_CONTEXT.md            # Original project overview
├── main.py                       # FastAPI application entrypoint
├── requirements.txt              # Core python dependencies
├── anromi.db                     # SQLite local development database
├── docs/
│   └── roadmap/                  # Detailed Version Roadmaps (v0.1.0 to v0.4.0)
│       ├── v0.1.0_core_engine.md
│       ├── v0.2.0_roots_physique_soul.md
│       ├── v0.3.0_alchemy_forging_economy.md
│       └── v0.4.0_tribulations_open_world.md
├── core/                         # Configuration, constants & database session
│   ├── config.py
│   └── database.py
├── models/                       # SQLAlchemy Database Models
│   ├── realm.py                  # 16-realm configurations & canonical metadata
│   ├── user.py                   # Cultivator character, lifespan, Qi stats, soul state
│   ├── inventory.py              # Items, pills, materials, artifacts (v0.3.0)
│   └── world.py                  # Nodes, biomes, leylines, connections (v0.4.0)
├── schemas/                      # Pydantic Schemas & DTOs
│   ├── cultivator.py             # User profile, meditation, breakthrough schemas
│   ├── game.py
│   └── world.py
├── services/                     # Pure Game Logic Engines
│   ├── cultivation_engine.py     # 16-realm Qi gathering, bottlenecks, breakthrough odds
│   ├── soul_engine.py            # Remnant soul survival, possession, reincarnation
│   ├── alchemy_engine.py         # Pill brewing, recipes, toxicity
│   ├── world_engine.py           # Node exploration, travel, encounter tables
│   └── tribulation_engine.py     # Multi-wave heavenly lightning simulations
└── api/                          # FastAPI REST Endpoints
    ├── routes_cultivator.py      # Register, profile, meditate, breakthrough
    ├── routes_world.py           # Map navigation, exploration, node interactions
    └── routes_inventory.py       # Bag, pill consumption, equipment
```
