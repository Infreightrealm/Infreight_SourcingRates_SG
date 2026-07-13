@echo off
:: This script runs the backend server in a loop and automatically checks for updates from GitHub on startup/restart.
:loop
echo ====================================================
echo [AUTO-UPDATE] Checking for latest code from GitHub...
echo ====================================================
git pull

echo ====================================================
echo [SERVER] Starting Infreight Sourcing Backend...
echo ====================================================
..\.venv\Scripts\python run_server.py

echo ====================================================
echo [SERVER] Server stopped. Restarting in 5 seconds...
echo Press Ctrl+C to terminate the auto-update loop.
echo ====================================================
timeout /t 5
goto loop
