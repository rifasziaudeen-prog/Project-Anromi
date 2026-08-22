# Anromi Frontend (Next.js)

Dark-xianxia web dashboard for Project Anromi. Single-page tabbed app:
🧘 Profile · ⛈️ Tribulation · 🎒 Bag & Craft · 🗺️ World · 👻 Soul · 📜 Chronicle sidebar.

## Run it

```bash
# 1) Start the game API (from the project root)
uvicorn main:app --port 8000

# 2) Start this dashboard
cd frontend
npm install        # once
npm run dev        # http://localhost:3000
```

Login = paste your **Discord user ID** (numbers only). Enable Developer Mode in Discord,
right-click your name → *Copy User ID*. It is stored in `localStorage` only.

## Configuration

`frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Reskinning (the one file you need)

All colors/fonts live as Tailwind v4 tokens in **`app/globals.css`** (`@theme` block):
`bg-ink-900`, `text-gold`, `border-gold/30`, `text-jade`, `text-blood`, `text-soul`,
`font-display`... Change a token value there and the whole game reskins.

## Structure

```
lib/api.ts      typed fetch wrappers — mirrors bot/api_client.py 1:1
lib/store.tsx   global state: identity, profile polling, toasts, act() helper
components/ui.tsx           Panel / Bar / Btn / Chip primitives
components/tabs/*.tsx       one component per tab
components/ChronicleFeed    polls /api/narration/events/recent
app/page.tsx                shell: entry gate + tabs + sidebar
```

**Zero game logic client-side** — every number comes from the FastAPI.

## Capacitor (Android) notes

- App is fully client-rendered ("use client") with fetch against an absolute API URL.
- For a device build, point `NEXT_PUBLIC_API_URL` at your LAN/hosted API and add the
  host to the Capacitor server config; no SSR features are used anywhere.
