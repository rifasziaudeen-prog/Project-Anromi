from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(override=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Anromi API"
    DATABASE_URL: str = "sqlite+aiosqlite:///./anromi.db"

    # ── Narration (The Heavenly Dao) — free-tier LLM fallback chains ──
    # Order matters: providers are tried in NARRATION_PROVIDERS order, and
    # within each provider its MODELS list is tried left-to-right before
    # falling through to the next provider.
    NARRATION_PROVIDERS: str = "groq,gemini,openrouter"
    GROQ_API_KEY: str = ""
    GROQ_MODELS: str = "openai/gpt-oss-120b,openai/gpt-oss-20b,groq/compound-mini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODELS: str = "gemini-3.7-flash,gemini-3.6-flash,gemini-3.5-flash,gemini-2.5-flash"
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODELS: str = "meta-llama/llama-3.1-8b-instruct:free"
    NARRATION_TIMEOUT_SECONDS: int = 20

    # ── Deployment / CORS ──
    # Comma-separated origins allowed to call this API from a browser.
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
