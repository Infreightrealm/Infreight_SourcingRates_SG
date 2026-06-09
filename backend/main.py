"""
Infreight Ocean Carrier Rate Automation — FastAPI Application.

Main entry point for the backend API server.
"""
import asyncio
import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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
        "carriers": [
            {
                "name": "Maersk",
                "code": "maersk",
                "path": "/vnc/maersk/vnc.html?autoconnect=true&resize=scale&reconnect=true&path=vnc/maersk/websockify",
                "ws_path": "/websockify/maersk"
            },
            {
                "name": "CMA CGM",
                "code": "cma",
                "path": "/vnc/cma/vnc.html?autoconnect=true&resize=scale&reconnect=true&path=vnc/cma/websockify",
                "ws_path": "/websockify/cma"
            },
            {
                "name": "ONE",
                "code": "one",
                "path": "/vnc/one/vnc.html?autoconnect=true&resize=scale&reconnect=true&path=vnc/one/websockify",
                "ws_path": "/websockify/one"
            },
            {
                "name": "Hapag-Lloyd",
                "code": "hapag",
                "path": "/vnc/hapag/vnc.html?autoconnect=true&resize=scale&reconnect=true&path=vnc/hapag/websockify",
                "ws_path": "/websockify/hapag"
            },
            {
                "name": "GreenX",
                "code": "greenx",
                "path": "/vnc/greenx/vnc.html?autoconnect=true&resize=scale&reconnect=true&path=vnc/greenx/websockify",
                "ws_path": "/websockify/greenx"
            }
        ] if is_prod else [],
        "vnc_path": "/vnc/vnc.html?autoconnect=true&resize=scale&reconnect=true", # Legacy fallback
        "message": "Multi-tab VNC viewer available." if is_prod else "VNC not available in local development mode.",
    }


@app.websocket("/websockify")
async def websockify_proxy(websocket: WebSocket):
    """Proxy WebSocket connections to legacy local x11vnc at localhost:5900."""
    await websocket.accept()
    try:
        reader, writer = await asyncio.open_connection("127.0.0.1", 5900)
    except Exception as e:
        print(f"[VNC Proxy] Failed to connect to x11vnc at 127.0.0.1:5900: {e}")
        await websocket.close(code=1011)
        return

    async def ws_to_tcp():
        try:
            while True:
                data = await websocket.receive_bytes()
                writer.write(data)
                await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def tcp_to_ws():
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                await websocket.send_bytes(data)
        except Exception:
            pass
        finally:
            try:
                await websocket.close()
            except Exception:
                pass

    await asyncio.gather(ws_to_tcp(), tcp_to_ws(), return_exceptions=True)


@app.websocket("/websockify/{carrier}")
async def websockify_carrier_proxy(websocket: WebSocket, carrier: str):
    """Proxy WebSocket connections to specific carrier x11vnc servers."""
    carrier_ports = {
        "maersk": 5900,
        "cma": 5901,
        "one": 5902,
        "hapag": 5903,
        "greenx": 5904
    }
    port = carrier_ports.get(carrier.lower(), 5900)
    
    await websocket.accept()
    try:
        reader, writer = await asyncio.open_connection("127.0.0.1", port)
    except Exception as e:
        print(f"[VNC Proxy] Failed to connect to x11vnc for {carrier} at 127.0.0.1:{port}: {e}")
        await websocket.close(code=1011)
        return

    async def ws_to_tcp():
        try:
            while True:
                data = await websocket.receive_bytes()
                writer.write(data)
                await writer.drain()
        except Exception:
            pass
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass

    async def tcp_to_ws():
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                await websocket.send_bytes(data)
        except Exception:
            pass
        finally:
            try:
                await websocket.close()
            except Exception:
                pass

    await asyncio.gather(ws_to_tcp(), tcp_to_ws(), return_exceptions=True)


# Mount noVNC static files if available
novnc_dir = "/usr/share/novnc"
if os.path.exists(novnc_dir):
    app.mount("/vnc", StaticFiles(directory=novnc_dir, html=True), name="vnc")
else:
    print("[WARN] /usr/share/novnc not found. noVNC web client won't be served via FastAPI.")


