@echo off
:loop
cls
echo ====================================================
echo [AUTO-UPDATE] Pulling latest code from GitHub...
echo ====================================================
git pull origin main
echo.
echo ====================================================
echo [SERVER] Starting Infreight Backend...
echo Press Ctrl+C once to trigger update and restart.
echo ====================================================
echo.
echo [PORT CHECK] Clearing any process bound to port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping process PID %%a on port 8000...
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

cd backend
:: Redirecting input via '< nul' bypasses the 'Terminate batch job (Y/N)' prompt
cmd /c "..\.venv\Scripts\python.exe run_server.py" < nul
cd ..
echo.
echo ====================================================
echo [SERVER] Stopped. Restarting loop in 3 seconds...
echo ====================================================
timeout /t 3
goto loop
