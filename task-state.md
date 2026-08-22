# Task State — Project Anromi
**Last Updated:** 2026-08-22 (Session 006)
**Purpose:** Live handoff file for all AI agents. Read this FIRST, then `CONTEXT.md`, then the relevant roadmap in `docs/roadmap/`. Update this file before you leave.

---

## 🎯 Current Objective
Direction B is now **COMPLETE** (narration ✅ Discord bot ✅ frontend ✅).
The next milestone is UNDECIDED — **ask the user to choose**:

**Option A — Combat & Sects (gameplay depth):**
1. Full turn-based combat engine (`services/combat_engine.py`): HP stat separate from Qi, techniques registry in `balance.py`, artifact `power` becomes real damage, bestiary tied to node danger tiers; replace `world_engine.resolve_ambush` with real fights.
2. Sect system: join/found, contribution points, sect quests, rivalries.

**Option B — Production Hardening:**
1. Real auth: Discord OAuth2 replacing raw discord_id entry (frontend + bot share it).
2. MongoDB Atlas migration (the SQLite→Mongo step promised in PROJECT_CONTEXT.md).
3. Hosting: deploy FastAPI + frontend + bot (VPS/Railway/Fly), HTTPS, secrets management.

**Option C — Balance Playtest Pass:** tune `core/balance.py` numbers from real play sessions, fix economy sinks/faucets, difficulty curve of tribulations by realm.

---

## 📊 Current Progress

### EVERYTHING THROUGH v0.6.0 COMPLETE ✅
- **Engine v0.1.0→v0.4.0**: realms, roots/soul/psychology, alchemy/forging/economy, tribulations/open world.
- **v0.5.0**: "The Heavenly Dao" narration (multi-model fallback chains per provider — Groq `openai/gpt-oss-120b → gpt-oss-20b → compound-mini`; Gemini `3.7-flash → 3.6 → 3.5 → 2.5`; OpenRouter free), GameEvent chronicle, full Discord bot w/ interactive tribulation buttons + announcer.
  - ⚠️ Gemini key in `.env` is still an OAuth token (`AQ.` prefix) — service logs a hint; **Groq key works and carries narration live** (verified in Session 006).
  - Root cause of earlier "invalid key" pain: an OS-level `GEMINI_API_KEY` env var shadowed `.env`. Fixed via `load_dotenv(override=True)`; pydantic Settings now `extra="ignore"` so bot vars coexist in one `.env`.
- **v0.6.0 (Session 006) — Frontend**: Next.js 16.3.2 (App Router, TS, Tailwind v4) in `frontend/`.
  - Single-page tabbed dashboard: Profile / Tribulation / Bag&Craft / World / Soul + Chronicle sidebar polling `/api/narration/events/recent`.
  - `lib/api.ts` typed client mirroring `bot/api_client.py`; `lib/store.tsx` state (localStorage identity gate, profile auto-poll 15s, toast system + `act()` helper, CustomEvent bridge for deep components).
  - Theme = Tailwind v4 tokens in ONE file (`app/globals.css` @theme block); reskin guide in `frontend/README.md`. Capacitor-ready (pure client rendering, absolute API URL).
  - npm 11 gotcha: create-next-app's install dies with `EALLOWSCRIPTS` under execution policy — template files survive; just run `npm.cmd install` inside `frontend/` manually.
  - Verified: `npm run build` clean (TS strict); E2E API 200 + frontend 200 serving ANROMI shell.
- **Tests: 82 passing** across 6 suites.

### Architecture invariants (do not break)
- Numbers/personas → `core/balance.py`; keys/models → `.env` only. Migrator auto-patches models at startup.
- Engines pure; routes own DB side-effects; bot & frontend own ZERO game logic.
- Windows note: use `npm.cmd` (PowerShell execution policy blocks `npm.ps1`).

---

## ⏭️ Next Task (for the incoming agent)
1. Ask user: Option A (combat/sects), B (hardening/deploy), or C (balance pass)?
2. If A: start `services/combat_engine.py` — add `hp` column (migrator handles), techniques list in balance, rewrite ambush callers, keep tribulations untouched.
3. If B: Discord OAuth first (frontend `/api/auth` proxy or direct), then Mongo migration via SQLAlchemy→Motor port of models (or keep SQL + document).
4. Run `python -m pytest tests/ -q` before/after changes; keep 82 green.

**On exit:** update Progress here, bump the `CONTEXT.md` ledger (Session #), add roadmap doc if starting a new milestone.
