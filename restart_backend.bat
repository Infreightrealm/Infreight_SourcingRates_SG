@echo off
title Infreight Backend Restarter
cd /d "%~dp0"

echo ========================================================
echo   Restarting Infreight Backend Server...
echo ========================================================
echo.

echo [1/3] Terminating any process running on Port 8000...
powershell -ExecutionPolicy Bypass -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /F /PID %%a >nul 2>&1
timeout /t 2 /nobreak >nul

where git >nul 2>&1
if %errorlevel%==0 (
    echo [2/3] Pulling latest updates from GitHub...
    git pull origin main
) else (
    echo [2/3] Git not installed — skipping git pull.
)

echo.
echo [3/3] Launching Infreight Backend Server (Port 8000)...
echo.
if exist .venv (
    .venv\Scripts\python.exe -c "import uvicorn" >nul 2>&1
    if errorlevel 1 (
        echo [INFO] Cleaning broken .venv folder...
        rmdir /s /q .venv >nul 2>&1
    )
)

set "PY_CMD=python"
if exist .venv\Scripts\python.exe (
    set "PY_CMD=..\.venv\Scripts\python.exe"
)

%PY_CMD% -c "import uvicorn" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing missing backend dependencies into Python...
    python -m pip install -r backend\requirements.txt
    python -m pip install uvicorn fastapi httpx websockets
)

cd backend && %PY_CMD% run_server.py

pause
