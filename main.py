from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.database import engine, Base
from core.config import settings
from core.migrations import run_startup_migrations

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and auto-patch missing columns onto old databases
    await run_startup_migrations(engine)
    yield
    # Shutdown
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="The Open-World Xianxia Text RPG Core Engine (Project Anromi)",
    version="0.7.0",
    lifespan=lifespan
)

# Browsers block cross-origin fetches (frontend :3000 → API :8000) without this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "project": "Project Anromi",
        "version": "0.4.0",
        "system": "16 Canonical Cultivation Realms Open-World Engine",
        "status": "online"
    }

# Cultivator Core API Router
from api import routes_cultivator, routes_soul, routes_inventory, routes_alchemy, routes_forging, routes_economy, routes_world, routes_tribulation, routes_narration
app.include_router(routes_cultivator.router, prefix="/api/cultivator", tags=["Cultivator"])
app.include_router(routes_soul.router, prefix="/api/soul", tags=["Soul & Permadeath"])
app.include_router(routes_inventory.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(routes_alchemy.router, prefix="/api/alchemy", tags=["Alchemy (Dan Dao)"])
app.include_router(routes_forging.router, prefix="/api/forging", tags=["Forging (Qi Dao)"])
app.include_router(routes_economy.router, prefix="/api/economy", tags=["Economy"])
app.include_router(routes_world.router, prefix="/api/world", tags=["World"])
app.include_router(routes_tribulation.router, prefix="/api/tribulation", tags=["Heavenly Tribulation"])
app.include_router(routes_narration.router, prefix="/api/narration", tags=["Narration & Events"])
