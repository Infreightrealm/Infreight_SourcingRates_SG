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
