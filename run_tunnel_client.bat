@echo off
title Infreight Railway Cloud Tunnel Client
cd /d "%~dp0"

echo ========================================================
echo   Starting Infreight Railway Cloud Tunnel Client...
echo ========================================================
echo.

set RELAY_DOMAIN=%1

if "%RELAY_DOMAIN%"=="" (
    if exist tunnel_config.txt (
        set /p RELAY_DOMAIN=<tunnel_config.txt
    )
)

if "%RELAY_DOMAIN%"=="" (
    echo.
    echo Please paste your Railway Tunnel Relay domain from Railway Dashboard:
    echo (Example: https://your-relay-service.up.railway.app)
    echo.
    set /p RELAY_DOMAIN="Railway Domain: "
)

if not "%RELAY_DOMAIN%"=="" (
    echo %RELAY_DOMAIN%> tunnel_config.txt
)

echo.
echo Connecting using domain: %RELAY_DOMAIN%
echo.

if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe scripts\tunnel_client.py --relay %RELAY_DOMAIN%
) else if exist backend\.venv\Scripts\python.exe (
    backend\.venv\Scripts\python.exe scripts\tunnel_client.py --relay %RELAY_DOMAIN%
) else (
    python scripts\tunnel_client.py --relay %RELAY_DOMAIN%
)

pause
