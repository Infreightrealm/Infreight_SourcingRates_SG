"""
Wrapper script to set Windows event loop policy before starting Uvicorn.
This ensures Playwright browser automation works on Windows.
"""
import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to preserve event loop policy
    )
