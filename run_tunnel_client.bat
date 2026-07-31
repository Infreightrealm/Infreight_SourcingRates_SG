@echo off
title Infreight Railway Cloud Tunnel Client
cd /d "%~dp0"

echo ========================================================
echo   Starting Infreight Railway Cloud Tunnel Client...
echo ========================================================
echo.

if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe scripts\tunnel_client.py %*
) else if exist backend\.venv\Scripts\python.exe (
    backend\.venv\Scripts\python.exe scripts\tunnel_client.py %*
) else (
    python scripts\tunnel_client.py %*
)

pause
