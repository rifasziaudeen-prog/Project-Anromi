"""
Anromi Discord Bot entrypoint.
1) Start the API:        uvicorn main:app
2) Fill .env:            DISCORD_BOT_TOKEN, API_BASE_URL, ANNOUNCE_CHANNEL_ID (optional)
3) Run:                  python run_bot.py
"""
from dotenv import load_dotenv

load_dotenv()

from bot.config import DISCORD_BOT_TOKEN  # noqa: E402  (after load_dotenv)
import bot.main as bot_module             # noqa: E402

if not DISCORD_BOT_TOKEN:
    raise SystemExit("DISCORD_BOT_TOKEN missing — set it in .env (see .env.example).")

bot_module.bot.run(DISCORD_BOT_TOKEN)
