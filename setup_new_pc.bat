@echo off
title Infreight New PC Setup Assistant
cd /d "%~dp0"

echo ========================================================
echo   Infreight Local Backend - New PC Setup Assistant
echo ========================================================
echo.

echo [1/3] Creating Python Virtual Environment (.venv)...
if not exist .venv (
    python -m venv .venv
)

echo.
echo [2/3] Installing Python Dependencies from backend/requirements.txt...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
pip install httpx websockets

echo.
echo [3/3] Installing Playwright & Patchright Stealth Browsers...
python -m playwright install chromium
python -m patchright install chromium

echo.
echo ========================================================
echo   SETUP COMPLETE! 🚀
echo ========================================================
echo.
echo To run your local backend on this new PC:
echo   1. Double-click run_live_loop.bat     (Starts local Python server)
echo   2. Double-click run_tunnel_client.bat   (Connects to Railway Cloud)
echo.
pause
