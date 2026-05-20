"""
Infreight Ocean Carrier Rate Automation — FastAPI Application.

Main entry point for the backend API server.
"""
import asyncio
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Fix for Windows: Use ProactorEventLoop for subprocess support (required for Playwright)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

load_dotenv()

from models.database import init_db
from api.rate_search_routes import router as rate_search_router
from api.port_routes import router as port_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print("[*] Starting Infreight Rate Automation API...")
    await init_db()
    print("[OK] Database tables created/verified")
    mock_mode = os.getenv("USE_MOCK_CARRIERS", "true").lower() in ("true", "1", "yes")
    print(f"[MODE] Mock mode: {'ENABLED' if mock_mode else 'DISABLED - using live connectors'}")
    yield
    print("[*] Shutting down...")


app = FastAPI(
    title="Infreight Ocean Carrier Rate Automation",
    description="Internal API for searching and comparing ocean freight rates across carriers.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rate_search_router)
app.include_router(port_router)


@app.get("/health")
async def health():
    mock_mode = os.getenv("USE_MOCK_CARRIERS", "true").lower() in ("true", "1", "yes")
    return {
        "status": "healthy",
        "service": "Infreight Rate Automation",
        "mock_mode": mock_mode,
    }


@app.get("/api/vnc-status")
async def vnc_status():
    """Check if the VNC viewer is available (production only, where Xvfb runs)."""
    is_prod = os.name != "nt"
    return {
        "available": is_prod,
        "vnc_path": "/vnc/vnc.html?autoconnect=true&resize=scale&reconnect=true",
        "message": "VNC viewer available — use the Live Browser View to interact with carrier portals."
        if is_prod
        else "VNC not available in local development mode.",
    }

