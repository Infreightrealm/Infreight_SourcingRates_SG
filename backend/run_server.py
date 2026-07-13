import asyncio
import sys
import uvicorn

if sys.platform == "win32":
    # Monkeypatch to prevent Uvicorn from overriding the ProactorEventLoop
    asyncio.WindowsSelectorEventLoopPolicy = asyncio.WindowsProactorEventLoopPolicy
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

if __name__ == "__main__":
    import os
    print("[SERVER] Starting server without --reload to maintain ProactorEventLoop for Playwright.")
    try:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
    finally:
        os._exit(0)
