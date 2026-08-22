import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

_raw_channel = os.getenv("ANNOUNCE_CHANNEL_ID", "").strip()
ANNOUNCE_CHANNEL_ID = int(_raw_channel) if _raw_channel.isdigit() else None

ANNOUNCE_POLL_SECONDS = int(os.getenv("ANNOUNCE_POLL_SECONDS", "30"))
