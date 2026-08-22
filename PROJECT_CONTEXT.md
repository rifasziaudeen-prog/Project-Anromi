# Project Anromi: Cross-Platform AI Gaming & Influencer Ecosystem
**Agent Context Document**

Welcome, fellow Agent! This document contains the architectural blueprint, lore, and current progress for Project Anromi. Your goal is to help build out specific phases of this ecosystem.

## 🏗️ Architecture Blueprint
Project Anromi is a decoupled ecosystem where multiple clients interact with a central Python API.

- **Central Brain (Completed):** FastAPI backend running Python. Currently using SQLite (SQLAlchemy) for prototyping, ready to migrate to MongoDB Atlas. Handles all secure game logic, stats, and progression.
- **Frontend (Pending):** Next.js / Vite web application for interactive gameplay. Will be wrapped in Capacitor for Android mobile deployment.
- **Discord Bot (Pending):** A `discord.py` bot that taps into the FastAPI server to trigger community alerts, global world bosses, and text-based gameplay.
- **Vtuber / Streamer UI (Pending):** Ciel's live persona. An automated system that reads database events and uses Groq + TTS to react live on a Twitch stream.

## 🐉 Core Lore: Xianxia Cultivation System
The game is based on classic Xianxia tropes:
- **Realms:** Qi Condensation -> Foundation Establishment -> Core Formation -> Nascent Soul -> Soul Formation.
- **Spiritual Roots:** Mortal, Earth, Heaven, Divine. Determines passive spiritual energy recovery.
- **Mechanics:** Players must meditate to passively gather Spiritual Energy. To breakthrough to the next stage/realm, they must reach the bottleneck (90% energy) and shatter it.

## ✅ Current Progress (Phase 1 Completed)
The foundation of the FastAPI backend is finished.
- `main.py` entrypoint is live.
- SQLite Database is configured with SQLAlchemy.
- `models/user.py` contains the Cultivator state (realm, stage, roots, energy).
- `api/routes_game.py` has working endpoints for `/auth`, `/meditate`, and `/breakthrough`.
- `services/game_logic.py` securely calculates energy regeneration and breakthrough odds.

## 📋 Agent To-Do List (Available Tasks)
If you have been summoned to work on this project, pick a phase below:

### Phase 2: The Next.js / React Native Frontend
- [ ] Scaffold a Next.js (or Vite + React) frontend.
- [ ] Create a dark-fantasy Xianxia themed UI (using Tailwind or raw CSS).
- [ ] Build a dashboard that fetches the user's stats from the FastAPI `GET /api/user/{id}` endpoint.
- [ ] Implement buttons that trigger `POST /api/meditate` and `POST /api/breakthrough` and visually update the UI.
- [ ] Prepare the web app to be wrapped in Capacitor for Android deployment.

### Phase 3: The Discord Bot Client
- [ ] Initialize a `discord.py` bot.
- [ ] Do NOT put game logic in the bot. The bot must make HTTP requests (using `aiohttp`) to the FastAPI backend to fetch user stats and trigger actions.
- [ ] Create commands: `/cultivate` (calls `/meditate`), `/breakthrough`, and `/stats`.

### Phase 4: Ciel's AI Integration (The Groq Router)
- [ ] In the FastAPI backend, implement `services/groq_service.py`.
- [ ] Write prompt templates that pass the user's breakthrough events into Groq.
- [ ] Expose an endpoint `POST /api/narrate` that returns a structured, dynamic, in-character narration of the cultivation event.
